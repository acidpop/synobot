#-*- coding: utf-8 -*-
import json
import enum

import single
from LogManager import log

task_list_file = "taskdata.json"


class TASK_TYPE(enum.IntEnum):
    TITLE = 0
    SIZE = 1
    USER = 2
    STATUS = 3

class TaskMgr(single.SingletonInstane):

    # DS Download Task Dictionary
    # Structure { task_id : [title, size, user, status] }
    task_data = {}
    noti_callback = None

    def AddNotiCallback(self, fn):
        self.noti_callback = fn

    # 
    def LoadFile(self):
        # Json 문자열을 가져와 Dictionary 로 변환
        #json_data = None
        try:
            if not self.task_data:
                with open( task_list_file ) as json_file:
                    self.task_data = json.load(json_file)
                    #self.task_data = json.loads(json_data)
        except:
            log.info('taskdata.json file open error')

    def SaveTask(self):
        # Dictionary 를 json으로 변환 후 json 문자열을 저장
        #json_val = json.dumps(self.task_data)

        with open( task_list_file, 'w' ) as json_file:
            json.dump(self.task_data, json_file, ensure_ascii=False, sort_keys=True)


    def InsertOrUpdateTask(self, task_id, title, size, user, status):
        task_list = []
        #log.info("Insert or update task")

        if task_id not in self.task_data :
            # 최초 등록
            task_list = [title, size, user, status]
            self.task_data[task_id] = task_list
            log.info("insert task : %s, %s", task_id, title)

            if self.noti_callback != None:
                self.noti_callback(task_id, title, size, user, status)

            self.SaveTask()

        else:
            ##
            task_list = self.task_data[task_id]

            old_status = task_list[TASK_TYPE.STATUS]

            if old_status != status:
                log.info("status change (%s -> %s, update task", old_status, status)
                task_list = [title, size, user, status]
                self.task_data[task_id] = task_list
                log.info("update task : %s, %s", task_id, title)
                # 기존 상태 값과 현재 상태값이 다른 경우 콜백 호출
                if self.noti_callback != None:
                    self.noti_callback(task_id, title, size, user, status)

                self.SaveTask()

    # 작업 중 삭제 된 Task 에 대한 예외 처리 필요
    def CheckRemoveTest(self, task_list):
        temp_task = {}
        # self.task_data 를 임시 dict 로 저장, 구조는 key  : exists flag (true, flase)
        for key in self.task_data.keys():
            temp_task[key] = False

        # 인자로 넘어온 task_list 를 loop 돌면서 temp_task 에 True 세팅
        for task_id in task_list:
            temp_task[task_id] = True

        # temp_task 를 loop 돌면서 Value 가 False 이면서 status 가 finished 가 아닌 Task 는 다운로드 취소 콜백 호출 후 task_data 에서 삭제한다
        delete_task_list = []
        for key, value in temp_task.items():
            if value == False:
                remove_task_list = self.task_data[key]

                if remove_task_list != None and self.noti_callback != None and remove_task_list[TASK_TYPE.STATUS] != 'finished':
                    self.noti_callback(key, remove_task_list[TASK_TYPE.TITLE], remove_task_list[TASK_TYPE.SIZE], remove_task_list[TASK_TYPE.USER], 'delete')
                
                delete_task_list.append(key)

        for task_id in delete_task_list:
            log.info("delete task : %s", task_id)
            del self.task_data[task_id]

        self.SaveTask()


