
import pymysql
import sys
import os
from os.path import isfile, isdir, join, splitext
# import geopandas
from nick_code.data_preprocess import data_preprocess
import shapefile
from json import dumps
import json
import pygeoif
from nick_code.data_preprocess import data_preprocess
import json
import osgeo as ogr,osr
from functools import partial
import pyproj
# import shapely.geometry
# import shapely.ops
import get_db
db = get_db.getDB()
conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
cursor = conn.cursor()
cursor1 = conn.cursor()

cursor.execute("select navtex_s124_id from s124_xml where topic like 'FIRE PRACTICES' or topic like 'GUNNERY' or topic like 'MILITARY EXERCISES'")
id_all = cursor.fetchall()

csv_text=''

for i in id_all:
    sql = "select ST_AsText(wkt) from geo_table where navtex_s124_id = %s "
    cursor.execute(sql,(i[0]))
    wkt = cursor.fetchall()
    # print(wkt[0])
    for j in wkt:

        print(j)
        csv_text = j[0] +"\n"+ csv_text

with open("tmmmp.csv", 'a') as f:
    f.writelines(csv_text)