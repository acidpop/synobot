#-*- coding: utf-8 -*-
import os
import single
import json

import BotConfig
from LogManager import log


class synobotLang(single.SingletonInstane):
    _instance = None
    lang_json = None

    #cfg = BotConfig.BotConfig().instance()
    #cfg = BotConfig()
    cfg = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kars):
        cls._instance = cls(*args, **kars)
        cls.instance = cls._getInstance
        return cls._instance

    def __init__(self):
        self.cfg = BotConfig.BotConfig().instance()

        self.LoadLangFile()

    def LoadLangFile(self):
        cur_path = os.getcwd()
        lang_name = self.cfg.GetSynobotLang()
        
        lang_path = cur_path + '/' + lang_name + '.json'

        # 사용자 지정한 로컬라이징 파일이 없으면 기본값으로 ko_kr.json 으로 작동
        if os.path.exists(lang_path) == False:
            lang_path = cur_path + '/ko_kr.json'

        log.info('Localing language : %s', lang_path)

        try:
            with open( lang_path) as json_file:
                self.lang_json = json.load(json_file)
        except:
            #log.info("synobot Language file loading fail")
            #print("load lang fail")
            log.info('synobot localizing file load fail, file path:%s', lang_path)

    def GetJson(self):
        return self.lang_json

    def GetBotHandlerLang(self, key):
        if self.lang_json["bothandler"].get(key):
            return self.lang_json["bothandler"].get(key)
        
        msg = "Unknown language key : %s" % (key)
        return msg

    def GetSynoDsLang(self, key):
        if self.lang_json["synods"].get(key):
            return self.lang_json["synods"][key]

        msg = "Unknown language key : %s" % (key)
        return msg

    def GetSynoErrorLang(self, key):
        if self.lang_json["syno_error"].get(key):
            return self.lang_json["syno_error"].get(key)

        msg = "Unknown language error key : %s" % (key)
        return msg

    def GetSynoAuthErrorLang(self, key):
        if self.lang_json["syno_auth_error"].get(key):
            return self.lang_json["syno_auth_error"].get(key)
        
        if self.lang_json["syno_error"].get(key):
            return self.lang_json["syno_error"].get(key)

        errstr = 'Unknown Auth Error Code : %s' % (key)
        return errstr

    def GetSynoTaskErrorLang(self, key):
        if self.lang_json["syno_task_error"].get(key):
            return self.lang_json["syno_task_error"].get(key)
        
        if self.lang_json["syno_error"].get(key):
            return self.lang_json["syno_error"].get(key)

        errstr = 'Unknown Auth Error Code : %s' % (key)
        return errstr



