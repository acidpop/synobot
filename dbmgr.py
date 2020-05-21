#-*- coding: utf-8 -*-

import sqlite3
from threading import Lock
import json
from datetime import datetime
import single
from LogManager import log

# SynoBot Sqlite database manager

# SQlite DB File Name
dbfile = "synobot.db"

# Table Schema
dsdownload_table = """
CREATE TABLE IF NOT EXISTS dsdownload(task_id TEXT, title TEXT, size INTEGER, user TEXT, status TEXT, workdate TEXT, PRIMARY KEY(task_id) );
"""

dsdownload_event_table = """
CREATE TABLE IF NOT EXISTS dsdownload_event(task_id TEXT, title TEXT, size INTEGER, user TEXT, status TEXT, isread INTEGER, PRIMARY KEY(task_id) );
"""

# 1. 최초 insert 시에는 use_yn 을 0으로 세팅
# 2. insert or replace 구문으로 수행시 다음 조건에 해당 하면
#    dsdownload_event table 에 Task 데이터를 insert 하고 isread 값을 0으로 한다.
#     조건 1 : Task ID 가 존재
#     조건 2 : Size 가 0 이상
#     조건 3 : status 값이 기존 데이터와 다른 경우

# 3. dsdownload_event 콜백에서 status 가 finished 가 되면 dsdownload 테이블의 데이터를 delete 한다
dsdownload_insert_trigger = """
CREATE TRIGGER IF NOT EXISTS ds_chk 
BEFORE INSERT ON dsdownload
WHEN
    NEW.status <> (SELECT status FROM dsdownload WHERE task_id = NEW.task_id)
BEGIN
    INSERT INTO dsdownload_event VALUES(NEW.task_id, NEW.title, NEW.size, NEW.user, NEW.status, 0);
END;
"""


dsdownload_delete_trigger = """
CREATE TRIGGER IF NOT EXISTS ds_delete
AFTER DELETE on dsdownload
BEGIN
    DELETE FROM dsdownload_event WHERE task_id = OLD.task_id;
END;
"""

class DBMgr(single.SingletonInstane):
    # 
    con = None
    cur = None
    lock = None

    def Init(self):
        self.lock = Lock()
        self.con = sqlite3.connect(":memory:", check_same_thread=False)
        #self.con = sqlite3.connect(dbfile, check_same_thread=False)

        # 컬럼명으로 접근 하기 위한 세팅
        self.con.row_factory = sqlite3.Row

        #self.RegiTriggerFunction()

        self.cur = self.con.cursor()
        self.CreateSynobotTable()

        log.info("SQLite DB Init")
        

    def ChkDBConnection(self):
        if self.con == None:
            self.Init()

    #def RegiTriggerFunction(self):
    #    self.con.create_function("ds_update_event", 5, self.ds_update_event)

    def CreateSynobotTable(self):

        self.ChkDBConnection()

        # Create Table
        self.cur.execute(dsdownload_table)
        self.cur.execute(dsdownload_event_table)

        # Create Trigger
        self.cur.execute(dsdownload_insert_trigger)
        self.cur.execute(dsdownload_delete_trigger)

        self.con.commit()

        return True

    def InsertTask(self, task_id, title, size, user, status):
        self.ChkDBConnection()

        log.info('Insert Task : %s, %s' % (task_id, title) )
        insert_time = datetime.now().strftime("%B %d, %Y %I:%M%p")
        insert_query = "INSERT OR REPLACE INTO dsdownload values (?, ?, ?, ?, ?, ?);"

        self.cur.execute(insert_query, (task_id, title, size, user, status, insert_time))

        insert_event_query = "INSERT OR IGNORE INTO dsdownload_event VALUES ('%s', '%s', '%s', '%s', '%s', 0);" % (task_id, title, size, user, status)
        self.cur.execute(insert_event_query)

        self.con.commit()

    def SetUseTask(self, task_id):
        self.ChkDBConnection()

        update_query = "UPDATE dsdownload_event SET isread = 1 WHERE task_id = '%s';" % (task_id)
        log.info(update_query)
        self.cur.execute(update_query)
        self.con.commit()

    def DeleteTask(self, task_id):
        self.ChkDBConnection()

        log.info('Delete Task : %s' % (task_id) )
        delete_query = "DELETE FROM dsdownload WHERE task_id = '%s';" % (task_id)
        self.cur.execute(delete_query)
        self.con.commit()

    def DeleteTaskNotInList(self, data_list):
        task_list = []

        log.info("Delete Task Not In List")

        if len(data_list) <= 0:
            log.info("Delete Task data list is 0")
            return

        for item in data_list:
            task_list.append(item['task_id'])

        delete_query = "DELETE FROM dsdownload WHERE task_id NOT IN ({seq})".format(seq=','.join(['?']*len(task_list)))
        #task_list_str = ','.join("'{0}'".format(e) for e in task_list)
        #delete_query = "DELETE FROM dsdownload WHERE task_id NOT IN (%s);" % (task_list_str)
        log.info(delete_query)

        self.cur.execute(delete_query, (task_list) )
        self.con.commit()

    def GetTaskList(self):
        self.ChkDBConnection()

        with self.lock:
            data_list = []
            task_query = "SELECT * FROM dsdownload_event WHERE isread = 0;"
            self.cur.execute(task_query)

            #if self.cur.rowcount <= 0:
            #    print('no data')
            #    return None

            rows = self.cur.fetchall()
            # task_id
            # title
            # size
            # user
            # status
            # workdate
            for row in rows:
                data = dict()
                data['task_id'] = row['task_id']
                data['title'] = row['title']
                data['size'] = row['size']
                data['user'] = row['user']
                data['status'] = row['status']
                data_list.append(data)

        return data_list

    #def ds_update_event(self, task_id, title, user, size, status):
    #    return True
