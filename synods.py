#-*- coding: utf-8 -*-
import os
import shutil
import requests
import json
import telegram

import single
import CommonUtil
import bothandler
import taskmgr
import BotConfig
import synobotLang

from LogManager import log



# Synology Download Station Handler

# sqlite Structure

#import os
#print(os.environ.get('DSM_'))

# Task Status : waiting, downloading, paused, finishing, finished, hash_checking, seeding, filehosting_waiting, extracting, error

# 1. Login
# 2. Task List
# 3. Create (File, Magnet)
# 4. Auto Delete (Optional)
# 5. SQLite insert or replace -> Trigger

class SynoDownloadStation(single.SingletonInstane):

    auth_cookie = None
    theTaskMgr = taskmgr.TaskMgr().instance()
    dsm_id = ''
    dsm_pw = ''
    dsm_otp = ''
    cfg = None
    lang = None
# 구현 대상
# 1. Task List 가져오기
# 2. Magnet 등록 하기
# 3. Torrent File 등록 하기
    def __init__(self, *args, **kwars):
        self.theTaskMgr.AddNotiCallback(self.TaskNotiCallback)
        self.theTaskMgr.LoadFile()
        self.cfg = BotConfig.BotConfig().instance()
        self.lang = synobotLang.synobotLang().instance()
        return

    def SendNotifyMessage(self, msg, ParseMode = None):
        noti_list = self.cfg.GetNotifyList()

        bot = bothandler.BotHandler().instance().bot

        for chat_id in noti_list:
            if ParseMode == 'mark':
                bot.sendMessage(chat_id, msg, parse_mode = telegram.ParseMode.MARKDOWN)
            elif ParseMode == 'html':
                bot.sendMessage(chat_id, msg, parse_mode = telegram.ParseMode.HTML)
            else:
                bot.sendMessage(chat_id, msg)

    def ChkTaskResponse(self, result_json, log_body):
        if not result_json:
            log.info('check response fail, result json data is empty')
            return False

        try:
            if result_json['success'] == True:
                return True

            errcode = result_json['error']['code']

            errstr = self.GetErrorTaskCode(errcode)
            msg = self.lang.GetBotHandlerLang('dsm_rest_api_fail') % (errstr, log_body)
            # msg = 'DSM 작업 실패\n%s\n%s' % (errstr, log_body)

            log.info(msg)
            log.info(result_json)

            if errcode != 100:
                self.SendNotifyMessage(msg)

            return False
        except:
            log.info('ChkTaskResponse Exception')
            return False

        return False

    def ChkAPIResponse(self, result_json, log_body):
        if not result_json:
            log.info('check API response fail, result json data is empty')
            return False

        try:
            if result_json['success'] == True:
                return True

            errcode = result_json['error']['code']

            errstr = self.GetErrorTaskCode(errcode)
            msg = self.lang.GetBotHandlerLang('dsm_rest_api_fail') % (errstr, log_body)
            # msg = 'DSM 작업 실패\n%s\n%s' % (errstr, log_body)

            log.info(msg)
            log.info(result_json)
            self.SendNotifyMessage(msg)

            return False
        except:
            log.info('ChkAPIResponse Exception')
            return False

        return False

    def DsmLogin(self, id, pw, otp_code = None):
        url = self.cfg.GetDSDownloadUrl() + '/webapi/auth.cgi'
        if not otp_code:
            # Not Use OTP Code
            log.info('without otp')
            params = {'api' : 'SYNO.API.Auth', 'version' : '3', 'method' : 'login' , 'account' : id, 'passwd' : pw, 'session' : 'DownloadStation', 'format' : 'cookie'}
        else:
            log.info('with otp')
            params = {'api' : 'SYNO.API.Auth', 'version' : '3', 'method' : 'login' , 'account' : id, 'passwd' : pw, 'session' : 'DownloadStation', 'format' : 'cookie', 'otp_code' : otp_code}

        log.info('Request url : %s', url)

        try:
            res = requests.get(url, params=params, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('Login|synology rest api request Connection Error')
            return False, None
        except:
            log.error('Login|synology requests fail')
            return False, None

        log.info('auth url requests succ')

        return True, res


    def GetTaskList(self):
        #url = 'https://downloadstation_dsm_url:9999/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list'

        if self.auth_cookie == None:
            return False

        params = {'api' : 'SYNO.DownloadStation.Task', 'version' : '3', 'method' : 'list'}

        url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/task.cgi'

        try:
            res = requests.get(url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('GetTaskList|synology rest api request Connection Error')
            return False
        except:
            log.error('GetTaskList|synology requests fail')
            return False

        

        if res.status_code != 200:
            log.warn("Get Task List Request fail")
            return False

        #print(res.content)

        json_data = json.loads(res.content.decode('utf-8'))

        if self.ChkTaskResponse(json_data, "GetTaskList Download station api fail") == False:
            self.auth_cookie = None
            return False


        exists_task_list = []
        for item in json_data['data']['tasks']:
            # log.info('GetTaskList : %s, %s, %s, %s, %s' % (item['id'], item['title'], CommonUtil.hbytes(item['size']), item['username'], item['status']) )
            # size 가 0 보다 큰 값인 경우에만 Torrent 정보가 정상적으로 확인 된다.
            exists_task_list.append(item['id'])
            tor_size = int(item['size'])
            if tor_size > 0:
                self.theTaskMgr.InsertOrUpdateTask(item['id'], item['title'], item['size'], item['username'], item['status'] )

        self.theTaskMgr.CheckRemoveTest(exists_task_list)

        if self.cfg.IsTaskAutoDel() == True:
            self.TaskAutoDelete(json_data)

        return True

    def GetTaskDetail(self):
        #url = 'https://downloadstation_dsm_url:9999/webapi/DownloadStation/task.cgi?api=SYNO.DownloadStation.Task&version=1&method=list&additional=detail,file,transfer'

        if self.auth_cookie == None:
            return False

        log.info('try task list detail')

        params = {'api' : 'SYNO.DownloadStation.Task', 'version' : '3', 'method' : 'list', 'additional' : 'detail,file,transfer'}

        url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/task.cgi'

        try:
            res = requests.get(url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('GetTaskList|synology rest api request Connection Error')
            return False
        except:
            log.error('GetTaskList|synology requests fail')
            return False

        log.info('complete task list detail')

        if res.status_code != 200:
            log.warn("Get Task List Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))

        if self.ChkAPIResponse(json_data, "Download station api fail") == False:
            self.auth_cookie = None
            log.info('ChkAPIResponse fail')
            return False

        # Json 분석 후 다운로드 리스트 보내기
        # 보낼 데이터, Task ID, 파일이름, 파일 크기, 다운로드 된 크기, 진행 상태, 업스피드, 다운스피드, 상태
        log.info("Task : %s", json_data['data']['tasks'])

        for item in json_data['data']['tasks']:
            # size 가 0 보다 큰 값인 경우에만 Torrent 정보가 정상적으로 확인 된다.
            tor_size = int(item['size'])
            # item 정보
            # id : Task ID
            # size : 파일 전체 크기
            # status : 진행 상태
            # title : 토렌트 제목

            # item['additional']['transfer']
            # size_downloaded : 다운로드 된 크기
            # size_uploaded : 업로드 된 크기
            # speed_download : 다운로드 속도(단위/s)
            # speed_upload : 업로드 속도 (단위/s)
            tor_id          = item['id']
            tor_status      = item['status']
            tor_title       = item['title']

            tor_size_download = 0
            tor_size_upload = 0
            tor_speed_down = 0
            tor_speed_up = 0

            if tor_size <= 0:
                self.SendTaskList(tor_id, tor_size, tor_status, tor_title, tor_size_download, tor_size_upload, tor_speed_down, tor_speed_up)
                return True
            
            # additional 아이템이 없다면 0 정보 전송
            if 'additional' in item == False:
                self.SendTaskList(tor_id, tor_size, tor_status, tor_title, tor_size_download, tor_size_upload, tor_speed_down, tor_speed_up)
                return True

            # transfer 아이템이 없다면 0 정보 전송
            if 'transfer' in item['additional'] == False:
                self.SendTaskList(tor_id, tor_size, tor_status, tor_title, tor_size_download, tor_size_upload, tor_speed_down, tor_speed_up)
                return True

            transfer_item = item['additional']['transfer']
            tor_size_download = transfer_item['size_downloaded']
            tor_size_upload = transfer_item['size_uploaded']
            tor_speed_down = transfer_item['speed_download']
            tor_speed_up = transfer_item['speed_upload']

            self.SendTaskList(tor_id, tor_size, tor_status, tor_title, tor_size_download, tor_size_upload, tor_speed_down, tor_speed_up)

        log.info('success Task List')

        return True

    def GetStatistic(self):
        # param = {'api' : 'SYNO.DownloadStation.Statistic', 'version' : '1', 'method' : 'getinfo'}
        # url = 'https://downloadstation_dsm_url:9999/webapi/DownloadStation/statistic.cgi'
        if self.auth_cookie == None:
            return False

        log.info('try get statistic')

        params =  {'api' : 'SYNO.DownloadStation.Statistic', 'version' : '1', 'method' : 'getinfo'}

        url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/statistic.cgi'

        try:
            res = requests.get(url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('GetStatistic|synology rest api request Connection Error')
            return False
        except:
            log.error('GetStatistic|synology requests fail')
            return False

        log.info('GetStatistic|complete get statistic')

        if res.status_code != 200:
            log.warn("GetStatistic|Get statistic Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))

        if self.ChkAPIResponse(json_data, "Download station api fail") == False:
            self.auth_cookie = None
            log.info('GetStatistic|ChkAPIResponse fail')
            return False

        # Data sample : {"data":{"speed_download":3496632,"speed_upload":0},"success":true}
        item = json_data.get('data')
        if item != None:
            download_speed = item['speed_download']
            upload_speed = item['speed_upload']
            self.SendStatistic(download_speed, upload_speed)
        else:
            log.info('GetStatistic|not found data, %s', res.content)

        return True

    def TaskAutoDelete(self, task_items):
        delete_task_id_arr = []

        for item in task_items['data']['tasks']:
            status = item['status']

            if status == 'finished' or status == 'seeding' or status == 'filehosting_waiting':
                # 완료, 보내기, 파일 호스팅 상태인 경우에만 작업 삭제 명령.
                log.info('Task Auto Delete, id:%s, title:%s, status:%s', item['id'], item['title'], item['status'])
                delete_task_id_arr.append(item['id'])
            
        # task array 에 아이템이 있다면 API 호출
        if len(delete_task_id_arr) > 0:
            task_id_list = ','.join(delete_task_id_arr)
            log.info('DS Delete API Call, Task ID : %s', task_id_list)
            self.DeleteTask(task_id_list)


    def CreateTaskForFile(self, file_path):
        create_url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/task.cgi'

        params2 = {'api' : 'SYNO.DownloadStation.Task', 'version' : '3', 'method' : 'create' }

        files = {'file' : open(file_path, 'rb')}

        try:
            log.info("url:%s, data:%s, files:%s, cookies:%s", create_url, params2, files, self.auth_cookie)
            res = requests.post(create_url, data=params2, files=files, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('CreateTaskForFile|synology rest api request Connection Error')
            return False
        except:
            log.error('CreateTaskForFile|synology requests fail')
            return False

        if res.status_code != 200:
            # print('request fail')
            log.warn("Create Task For File Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))
        if self.ChkAPIResponse(json_data, "Download station Create Task for file") == False:
            return False

        # Remove Torrent File
        files['file'].close()
        os.remove(file_path)
        log.info('Torrent File removed, file:%s', file_path)

        return True


    def CreateTaskForFileToWatchDir(self, file_path):
        watch_path = self.cfg.GetTorWatch()

        if len(watch_path) <= 0:
            log.info("watch path is not define")
            # DSM_WATCH 환경 변수 등록 알림, noti_torrent_watch_nothing

            msg = self.lang.GetBotHandlerLang('noti_torrent_watch_nothing')

            self.SendNotifyMessage(msg)

            return False

        try:
            shutil.move(file_path, watch_path)
        except FileNotFoundError:
            log.info('Torrent file move fail, No such file or directory')

            msg = self.lang.GetBotHandlerLang('noti_torrent_watch_mv_fail')
            self.SendNotifyMessage(msg)
            return False
        except:
            log.info('Torrent file move fail, error')

            msg = self.lang.GetBotHandlerLang('noti_torrent_watch_mv_fail')
            self.SendNotifyMessage(msg)
            return False

        log.info("Torrent file move to torrent watch directory, watch:%s", watch_path)

        return True


    # HTTP/FTP/magnet/ED2K link
    def CreateTaskForUrl(self, url):
        create_url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/task.cgi'

        params = {'api' : 'SYNO.DownloadStation.Task', 'version' : '3', 'method' : 'create' , 'uri' : url}

        try:
            res = requests.get(create_url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('CreateTaskForUrl|synology rest api request Connection Error')
            return False
        except:
            log.error('CreateTaskForUrl|synology requests fail')
            return False

        if res.status_code != 200:
            log.warn("Create Task For Url Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))
        if self.ChkAPIResponse(json_data, "Download station Create Task for url") == False:
            return False

        return True

    # Download Station Delete
    def DeleteTask(self, task_id):
        delete_url = self.cfg.GetDSDownloadUrl() + '/webapi/DownloadStation/task.cgi'

        params = {'api' : 'SYNO.DownloadStation.Task', 'version' : '3', 'method' : 'delete' , 'id' : task_id}

        try:
            res = requests.get(delete_url, params=params, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('DeleteTask|synology rest api request Connection Error')
            return False
        except:
            log.error('DeleteTask|synology requests fail')
            return False

        if res.status_code != 200:
            log.warn("Delete Task Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))
        if self.ChkAPIResponse(json_data, "Download station Delete Task") == False:
            return False

        return True

    def TaskNotiCallback(self, task_id, title, size, user, status):
        log.info("Task Noti")
        bot = bothandler.BotHandler().instance().bot

        if bot == None:
            log.info("Bot instance is none")
            return

        log.info('Task Monitor : %s, %s, %s, %s, %s' % (task_id, title, CommonUtil.hbytes(size), user, status) )
        #msg = '*상태* : %s\n*이름* : %s\n*크기* : %s\n*사용자* : %s' % ( self.StatusTranslate(status), title, CommonUtil.hbytes(size), user)
        msg = self.lang.GetBotHandlerLang('noti_torrent_status') % ( self.StatusTranslate(status), title, CommonUtil.hbytes(size), user)
        #self.SendNotifyMessage(msg, ParseMode = 'mark')
        self.SendNotifyMessage(msg)

    def SendTaskList(self, task_id, task_size, task_status, task_title, download_size, upload_size, download_speed, upload_speed):
        log.info("Task Noti")
        bot = bothandler.BotHandler().instance().bot

        if bot == None:
            log.info("Bot instance is none")
            return

        log.info('Task Detail : %s, %s, %s, %s, %s, %s, %s, %s' % ( task_id, task_title, CommonUtil.hbytes(task_size), self.StatusTranslate(task_status), CommonUtil.hbytes(download_size), CommonUtil.hbytes(upload_size), CommonUtil.hbytes(download_speed), CommonUtil.hbytes(upload_speed) ) )
        msg = self.lang.GetBotHandlerLang('noti_task_list') % ( task_id, task_title, CommonUtil.hbytes(task_size), self.StatusTranslate(task_status), CommonUtil.hbytes(download_size), CommonUtil.hbytes(upload_size), CommonUtil.hbytes(download_speed), CommonUtil.hbytes(upload_speed) )
        self.SendNotifyMessage(msg)

    def SendStatistic(self, download_speed, upload_speed):
        log.info("Statistic Noti")
        bot = bothandler.BotHandler().instance().bot

        if bot == None:
            log.info("Bot instance is none")
            return

        log.info('Statistic : %s, %s' % ( CommonUtil.hbytes(download_speed), CommonUtil.hbytes(upload_speed) ) )
        msg = self.lang.GetBotHandlerLang('noti_statistic') % ( CommonUtil.hbytes(download_speed), CommonUtil.hbytes(upload_speed) )
        self.SendNotifyMessage(msg)
        return


    def StatusTranslate(self, status):
        status_msg = ''
        try:
            status_msg = self.lang.GetSynoDsLang(status)
        except:
            status_msg = status

        return status_msg

    def GetErrorAuthCode(self, code):
        return self.lang.GetSynoAuthErrorLang( str(code) )

    def GetErrorTaskCode(self, code):
        return self.lang.GetSynoTaskErrorLang( str(code) )

"""
    # 해당 코드는 현재 작동 안함.
    def CreateTaskForFileDSM7(self, file_path):
        create_url = self.cfg.GetDSDownloadUrl() + '/webapi/entry.cgi'

        stat = os.stat(file_path)

        #torrent_file = open(file_path, 'rb')

        params2 = {'api' : 'SYNO.DownloadStation2.Task', 'version' : '2', 'method' : 'create' , 'type' : 'file', 'create_list' : True, 'destination' : '/volume1/download/torrent', 'username' : 'userid' , 'password' : 'userpassword', 'mtime' : stat.st_mtime, 'size' : stat.st_size}

        torrent_file = {'file' : open(file_path, 'rb')}
        

        try:
            log.info("url:%s, data:%s, files:%s, cookies:%s", create_url, params2, file_path, self.auth_cookie)
            res = requests.post(create_url, data=params2, files=torrent_file, cookies=self.auth_cookie, verify=self.cfg.IsUseCert())
        except requests.ConnectionError:
            log.error('CreateTaskForFile|synology rest api request Connection Error')
            return False
        except:
            log.error('CreateTaskForFile|synology requests fail')
            return False

        if res.status_code != 200:
            # print('request fail')
            log.warn("Create Task For File Request fail")
            return False

        json_data = json.loads(res.content.decode('utf-8'))
        if self.ChkAPIResponse(json_data, "Download station Create Task for file") == False:
            return False

        # Remove Torrent File
        torrent_file['file'].close()
        #torrent_file.close()
        os.remove(file_path)
        log.info('Torrent File removed, file:%s', file_path)

        return True
    """

