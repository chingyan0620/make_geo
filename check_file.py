import  pymysql 
from selenium import webdriver
import time
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import ast
import get_db
db = get_db.getDB()
conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
cursor = conn.cursor()


keyword = "fire"
day_num = -20


today = date.today()
stop_day = today.strftime("%Y-%m-%d")
dt = datetime.datetime.strptime(stop_day, "%Y-%m-%d")
start_day = (dt + datetime.timedelta(days=day_num)).strftime("%Y-%m-%d")

sql_str = """SELECT DISTINCT  navtex_s124_id FROM showtime WHERE show_time>=%s and show_time<=%s"""
cursor.execute(sql_str,(start_day,stop_day))
aa = cursor.fetchall()

cursor.execute("""SELECT navtex_s124_id FROM navtex_content""")
bb = cursor.fetchall()

show_time_list =[]
for i in aa:
    show_time_list.append(i[0])

content_id_list = []
for i in bb:
    content_id_list.append(i[0])

not_in_content = []
for i in show_time_list:
    if i not in content_id_list:
        not_in_content.append(i)
print(not_in_content)
