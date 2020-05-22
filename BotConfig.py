#-*- coding: utf-8 -*-

import sys
import os
import socket
import single

class BotConfig(single.SingletonInstane):
    
    # 알림을 받을 Telegram 사용자의 Chat ID리스트 (, 기호로 구분)
    notify_chat_id_list = None
    dsm_pw_chat_id = ""
    # DSM 로그인 ID
    dsm_id = ""
    # DSM 로그인 PW
    dsm_pw = ""
    # Telegram Bot Token
    bot_token = ""
    # BOT 명령에 유효한 Telegram 사용자 Chat ID
    valid_user_list = None
    # Log Size (단위:MB)
    log_size = 0
    # Log Rotation 개수
    log_count = 0
    # Synlogy DSM 접속 URL 또는 IP
    dsm_url = ''
    # Synology Download Station 의 포트
    ds_download_port = 80
    # Https SSL 인증서 불일치 무시 여부
    dsm_cert = True
    # 로그인 재시도 횟수
    dsm_retry_login = 10
    # 작업 완료시 자동 삭제 여부
    dsm_task_auto_delete = False
    # 로컬라이징
    synobot_lang = 'ko_kr'

    execute_path = ""
    host_name = ''

    # Https 사용시 인증서 무시 여부


    def __init__(self, *args, **kwargs):

        temp_notify_list = os.environ.get('TG_NOTY_ID', '12345678')
        if temp_notify_list.find(',') == -1:
            temp_notify_list += ', '
        self.notify_chat_id_list = eval(temp_notify_list)

        self.dsm_pw_chat_id = os.environ.get('TG_DSM_PW_ID', '12345678')

        self.dsm_id = os.environ.get('DSM_ID', '')
        self.bot_token = os.environ.get('TG_BOT_TOKEN', '186547547:AAEXOA9ld1tlsJXvEVBt4MZYq3bHA1EsJow')
        temp_valid_user = str(os.environ.get('TG_VALID_USER', '12345678,87654321'))
        if temp_valid_user.find(',') == -1:
            temp_valid_user += ', '
        self.valid_user_list = eval(temp_valid_user)
        
        self.log_size = int( os.environ.get('LOG_MAX_SIZE', '50') )
        self.log_count = int( os.environ.get('LOG_COUNT', '5') )

        self.dsm_url = os.environ.get('DSM_URL', 'https://DSM_IP_OR_URL')
        self.ds_download_port = os.environ.get('DS_PORT', '8000')

        # Https SSL 인증서 불일치 무시 여부
        temp_val = os.environ.get('DSM_CERT', '1')
        if temp_val == '0':
            self.dsm_cert = False

        self.dsm_retry_login = os.environ.get('DSM_RETRY_LOGIN', 10)

        temp_val = os.environ.get('DSM_AUTO_DEL', '0')
        if temp_val == '1':
            self.dsm_task_auto_delete = True

        self.synobot_lang = os.environ.get('TG_LANG', 'ko_kr')

        temp_path = os.path.split(sys.argv[0])
        self.execute_path = temp_path[0]

        self.host_name = socket.gethostname()

        # DSM_PW 환경변수가 있는 경우에는 Telegram 을 통해 암호를 입력 받는 과정을 생략 한다.
        self.dsm_pw = os.environ.get('DSM_PW', '')


    def GetNotifyList(self):
        return self.notify_chat_id_list

    def GetDsmPwId(self):
        return self.dsm_pw_chat_id

    def GetDsmId(self):
        return self.dsm_id

    def GetBotToken(self):
        return self.bot_token

    def GetValidUser(self):
        return self.valid_user_list

    def GetLogSize(self):
        return self.log_size

    def GetLogCount(self):
        return self.log_count

    def GetDSDownloadUrl(self):
        return self.dsm_url + ":" + self.ds_download_port

    def GetExecutePath(self):
        return self.execute_path

    def GetHostName(self):
        return self.host_name

    def GetDsmPW(self):
        return self.dsm_pw

    def SetDsmPW(self, pw):
        self.dsm_pw = pw

    def IsUseCert(self):
        return self.dsm_cert

    def GetDsmRetryLoginCnt(self):
        return int(self.dsm_retry_login)

    def IsTaskAutoDel(self):
        return self.dsm_task_auto_delete

    def GetSynobotLang(self):
        return self.synobot_lang

