
#-*- coding: utf-8 -*-
import sys
import time
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)

import single
import synods
import ThreadTimer
#import systemutil
import BotConfig
import synobotLang

from LogManager import log

# Valid User 구현

class BotHandler(single.SingletonInstane):

    ds = None
    BotUpdater = None
    bot = None

    cur_mode = ''

    cfg = None
    valid_users = None

    lang = None

    otp_input = False
    otp_code = None

    try_login_cnt = 0

    def InitBot(self):
        self.cfg = BotConfig.BotConfig().instance()
        self.valid_users = self.cfg.GetValidUser()

        self.lang = synobotLang.synobotLang().instance()

        log.info("Bot Token : %s", self.cfg.GetBotToken())
        updater = Updater(self.cfg.GetBotToken(), use_context=True)

        self.BotUpdater = updater
        self.bot = updater.bot

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))
        #dp.add_handler(CommandHandler("systeminfo", self.systeminfo))
        dp.add_handler(CommandHandler("dslogin", self.dslogin))

        # SynoBot Command
        """
        /dslogin
        /cancel
        /
        """

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.msg_handler))

        dp.add_handler(MessageHandler(Filters.document, self.file_handler))

        # log all errors
        dp.add_error_handler(self.error)

        self.ds = synods.SynoDownloadStation().instance()

        # Start the Bot
        updater.start_polling()

        # Download Station Task Monitor
        dsdown_task_monitor = ThreadTimer.ThreadTimer(10, self.ds.GetTaskList)

        dsdown_task_monitor.start()

        self.StartDsmLogin()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

    def CheckValidUser(self, chat_id):
        if not chat_id in self.valid_users:
            log.info("Invalid User : %s", chat_id)
            return False
        return True

    def StartInputLoginId(self):
        log.info('Start Input ID Flow')
        self.cur_mode = 'input_id'
        bot = self.BotUpdater.bot
        #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM 로그인 ID를 입력하세요")
        bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('input_login_id'))

    def StartInputPW(self):
        log.info("Start Input PW Flow")
        self.cur_mode = 'input_pw'
        bot = self.BotUpdater.bot
        #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM 로그인 비밀번호를 입력하세요\n비밀번호 메시지를 메시지 수신 후 삭제합니다")
        bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('input_login_pw'))
        # log.info('lang : %s', self.lang.GetBotHandlerLang('input_login_pw'))

    def StartInputOTP(self):
        log.info("Start Input OTP Flow")
        self.cur_mode = 'input_otp'
        bot = self.BotUpdater.bot
        #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM OTP에 표시된 숫자를 입력하세요")
        bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('input_login_otp'))

    def StartDsmLogin(self):
        retry_cnt = self.cfg.GetDsmRetryLoginCnt()

        bot = self.BotUpdater.bot

        # 재시도 횟수 까지 로그인을 시도하며, 횟수 초과시 프로그램 종료
        while self.try_login_cnt < retry_cnt:
            # 로그인 Flow
            # 1. dsm_id 값이 있는지 확인
            # 2. dsm_pw 값이 있는지 확인
            # 3. DS API Login 시도
            # 4. 결과 코드 조회
            # 4-1 반환된 rest api 의 content 값을 보고 판단.

            # step 1
            # dsm_id 가 비어 있는 경우
            if not self.cfg.GetDsmId():
                log.info('DSM ID is empty')
                self.StartInputLoginId()
                return False

            # step 2
            if not self.cfg.GetDsmPW():
                log.info('DSM PW is empty')
                self.StartInputPW()
                return False

            # step 3
            id = self.cfg.GetDsmId()
            pw = self.cfg.GetDsmPW()
            otp_code = self.otp_code
            res, content = self.ds.DsmLogin(id, pw, otp_code)

            # step 4
            if res == False:
                log.info('DSM Login fail, API request fail')
                # 3초 대기 후 재시도
                time.sleep(3)
                continue
            
            log.info('DSM Login check content json data')
            # step 4-1
            # rest api 의 내용 중 http status code 가 200이 아닌 경우 예외처리
            # status code 가 200 이면 수신 된 json 데이터를 가지고 예외 처리
            if content.status_code != 200:
                log.warn("DSM Login Request fail")
                # msg = '로그인 요청 실패\n, 응답 코드 : %d' % (res.status_code)
                msg = self.lang.GetBotHandlerLang('dsm_login_api_fail') % (res.status_code)
                
                bot.sendMessage(self.cfg.GetDsmPwId(), msg)
                time.sleep(3)
                continue

            # content 에서 json 데이터 파싱
            json_data = json.loads(content.content.decode('utf-8'))

            # json_data 가 None 이라면 DS API 이상, 재시도
            if json_data == None:
                log.info('DS API Response content is none')
                #bot.sendMessage(self.cfg.GetDsmPwId(), 'DS API 응답 데이터가 비어있습니다')
                bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_api_res_empty'))
                time.sleep(3)
                continue

            if json_data['success'] == False:
                log.info('DS API Response false')
                errcode = json_data['error']['code']
                
                # 105 세션 만료
                # 400 id 또는 암호 오류
                # 401 계정 비활성화
                # 402 2단계 인증 실패
                if errcode == 105:
                    log.info('105 error, session expired')
                    #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM Login 실패\n세션이 만료되었습니다.")
                    bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_session_expire'))
                    return False
                elif errcode == 400:
                    log.info('400 error, id or pw invalid')
                    #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM Login 실패\nID 또는 비밀번호가 다릅니다.")
                    bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_invalid_id_pw'))
                    self.StartInputPW()
                    return False
                elif errcode == 401:
                    log.info('401 error, account disabled')
                    #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM Login 실패\n비활성화 된 계정입니다.")
                    bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_account_disable'))
                    return False
                elif errcode == 402:
                    log.info('402 error, permission denied, try otp auth login')
                    self.StartInputOTP()
                    return False

            if json_data['success'] == True:
                log.info('DSM Login success')
                self.ds.auth_cookie = content.cookies
                self.try_login_cnt = 0
                # bot.sendMessage(self.cfg.GetDsmPwId(), 'DS Login 성공\nSynobot을 시작합니다.')
                bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_login_succ'))
                return True

            log.info('retry login... %d/%d', self.try_login_cnt, retry_cnt)
            self.try_login_cnt += 1


        #bot.sendMessage(self.cfg.GetDsmPwId(), "DSM Login에 실패 하였습니다.\n프로그램이 종료됩니다")
        bot.sendMessage(self.cfg.GetDsmPwId(), self.lang.GetBotHandlerLang('dsm_login_fail_exit'))
        log.info('DSM Login Fail!!')
        sys.exit()

        return False


    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, update, context):
        # Bot Start Message
        if self.CheckValidUser(update.message.from_user.id) == False:
            return

        update.message.reply_text('Hi!')


    def help(self, update, context):
        """Send a message when the command /help is issued."""
        if self.CheckValidUser(update.message.from_user.id) == False:
            return

        update.message.reply_text('Help!')

    #def systeminfo(self, update, context):
    #    if self.CheckValidUser(update.message.from_user.id) == False:
    #        return
    #    # /systeminfo Command
    #    sys_info = systemutil.GetTopProcess()
#
    #    update.message.reply_markdown(sys_info)

    def dslogin(self, update, context):
        if self.CheckValidUser(update.message.from_user.id) == False:
            return

        log.info("DSM Login Mode")

        #update.message.reply_text('로그인을 시도합니다')
        update.message.reply_text(self.lang.GetBotHandlerLang('dsm_try_login'))

        #self.cur_mode = 'input_id'
        #update.message.reply_text('로그인 ID를 입력하세요')
        #update.message.reply_text(self.lang.GetBotHandlerLang('input_login_id'))
        self.StartDsmLogin()

    def current_mode_handle(self, update, context):
        command = update.message.text

        if self.cur_mode == 'input_id':
            self.ds.dsm_id = command
            self.cur_mode = 'input_pw'
            #update.message.reply_text('로그인 비밀번호를 입력하세요')
            update.message.reply_text(self.lang.GetBotHandlerLang('input_login_pw'))
        elif self.cur_mode == 'input_pw':
            self.cfg.SetDsmPW(command)
            self.ds.dsm_pw = command
            self.cur_mode = ''

            update.message.delete()
            #update.message.reply_text('입력 된 암호 메시지를 삭제 하였습니다')
            update.message.reply_text(self.lang.GetBotHandlerLang('noti_delete_pw'))

            #self.ds.Login()
            self.StartDsmLogin()
        elif self.cur_mode == 'input_otp':
            self.ds.dsm_otp = command
            self.otp_code = command
            self.cur_mode = ''
            self.otp_input = True
            update.message.delete()
            #update.message.reply_text('입력 된 OTP 메시지를 삭제 하였습니다')
            update.message.reply_text(self.lang.GetBotHandlerLang('noti_delete_otp'))

            #self.ds.Login()
            self.StartDsmLogin()
        else:
            log.info('unknown current mode : %s', self.cur_mode)
            self.cur_mode = ''


    def msg_handler(self, update, context):

        log.info('current mode : %s', self.cur_mode)

        if self.cur_mode != 'input_pw' and self.cur_mode != 'input_otp':
            log.info("msg : %s", update.message.text)

        if self.CheckValidUser(update.message.from_user.id) == False:
            return

        command = update.message.text

        if self.cur_mode:
            log.info('try current mode handle')
            self.current_mode_handle(update, context)
        elif( command[0:8] == 'magnet:?'):
            log.info("Detected magnet link, Create Task URL for magnet")
            self.ds.CreateTaskForUrl(command)
            #update.message.reply_text('마그넷 링크를 등록하였습니다')
            update.message.reply_text(self.lang.GetBotHandlerLang('noti_magnet_link'))
        else:
            # Send Help Message
            #update.message.reply_text('지원 되지 않는 명령입니다')
            update.message.reply_text(self.lang.GetBotHandlerLang('noti_not_support_cmd'))


    def file_handler(self, update, context):
        if self.CheckValidUser(update.message.from_user.id) == False:
            return

        # 1. Get File Name
        file_name = update.message.document.file_name
        file_mime = update.message.document.mime_type
        file_path = file_name

        # 2. .torrent 파일인지 확인
        if( file_mime == 'application/x-bittorrent'):
            tor_file = update.message.document.get_file(timeout=5)
            tor_file.download(custom_path=file_path, timeout=5)
            self.ds.CreateTaskForFile(file_path)
            log.info("File Received, file name : %s", file_path)
            
            bot = self.BotUpdater.bot
            #msg = 'Torrent 파일(%s)을 등록 하였습니다' % (file_name)
            msg = self.lang.GetBotHandlerLang('noti_torrent_file') % (file_name)

            bot.sendMessage(self.cfg.GetDsmPwId(), msg)
        else:
            bot = self.BotUpdater.bot

            #msg = 'torrent 파일만 지원합니다, File : %s' % (file_name)
            msg = self.lang.GetBotHandlerLang('noti_not_torrent_file') % (file_name)

            bot.sendMessage(self.cfg.GetDsmPwId(), msg)


    def error(self, update, context):
        """Log Errors caused by Updates."""
        log.error('Update "%s" caused error "%s"', update, context.error)
        log.error("error")

