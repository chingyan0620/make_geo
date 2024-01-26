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
import get_db
db = get_db.getDB()
conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
cursor = conn.cursor()
cursor1 = conn.cursor()
cursor1.execute("select * from geo_table")
cursor.execute("select CONTENT from navtex_content")
row_all = cursor.fetchall()
num = 0
#-------------------------------------
# cursor.execute("select CONTENT from navtex_content WHERE navtex_s124_id ='0315.20'")
# row_all = cursor.fetchall()
# print(row_all)
#-------------------------------------
cursor1.execute("DROP TABLE IF EXISTS GEO_TABLE")
cursor1.execute("""CREATE TABLE GEO_TABLE (
        NAVTEX_S124_ID CHAR(20) NOT NULL,
        NUMBER_ID TEXT,
        GEO_INFORMATION TEXT,
        GEOJSON TEXT,
        WKT TEXT
        )""")
cursor1 = conn.cursor()
cursor1.execute("select * from geo_table")

commit_count = 0
for i in row_all:
    num = num + 1
    
    print(str(i[0]))
    with open("./nick_code/data/raw_data/tmp.txt","w") as f:
        f.writelines(i)
    path1=os.path.abspath('.')
    
    readpath = "./nick_code/data/raw_data/"
    savepath = "./nick_code/data/data_for_tagging/"
    pre = data_preprocess(readpath, savepath)
    msg = pre.get_file_msg("./nick_code/data/raw_data/tmp.txt")
    
    with open(savepath+"tmp_slip.txt",'w')as d:
        for j in msg:
            for k in j:
                d.write(k+"\n")
                
    result_path = "geo_result/"
    result_list = os.listdir(result_path)
    for j in result_list:
        os.remove(result_path + j)
    shp_path = "./nick_code/data/shapefile/tmp_shp/"
    shp_list = os.listdir(shp_path)
    for j in shp_list:
        os.remove(shp_path + j)
        


    # ----check shapefile generate ----#
    shp_list1 = os.listdir(shp_path)
    
    if shp_list1 == []:
        counter = 0
        while(counter < 10):
                
                os.system('python nick_code/main_tag.py')
                os.system('python nick_code/main_ext.py')
                print( isfile(shp_path))
                if os.listdir(shp_path) != []:
                    break
                counter += 1
                print("try to rebuilt shp " + str(counter) + " times!")
                if counter == 10:
                    with open("error_log.txt","a") as f1:
                        with open("./nick_code/data/raw_data/tmp.txt",'r')as d:
                            content = d.readlines()
                            f1.writelines(content)
                            f1.write("\n-------------------------------------------------------------")
    
    # ----get shapefile to other type ----#
    shp_list = os.listdir(shp_path)
    for f in shp_list:
        fullpath = shp_path + f
        if isfile(fullpath):
            print(splitext(f))
            if splitext(f)[1] == '.shp':

                # myshpfile = geopandas.read_file(fullpath)

                json_full_path = result_path + str(f)[:-4] +".geojson"
                # myshpfile.to_file( json_full_path , driver='GeoJSON')
                print("==============================")
                reader = shapefile.Reader(fullpath) 
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                # print(reader.shapes)
                buffer = []
                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    geom = sr.shape.__geo_interface__
                    buffer.append(dict(type="Feature", \
                        geometry=geom, properties=atr)) 

                # write the GeoJSON file

                geojson = open(json_full_path, "w")
                geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
                geojson.close()
                reader.close()





                json_text = open(json_full_path).read()
                # print(json_text)
                json_text1 = json.loads(json_text)
                print("==============================")
                # wkt = json_text['features'][2]['properties'][0]['Geometry']
                
                wkt = json_text1['features'][0]["properties"]["Geometry"]
                # print(str(wkt))
                name_shp = f.split('.')
                s124_id = "0" + name_shp[1] + "." + name_shp[0]
                print(s124_id)
                sql = "INSERT into geo_table(NAVTEX_S124_ID,NUMBER_ID,GEOJSON,WKT)VALUES(%s,%s,%s,%s)"
                cursor1.execute(sql,(s124_id,name_shp[2],json_text,wkt))


    

    # raw_text = open("./nick_code/data/raw_data/tmp.txt").read()
    text = open("./nick_code/data/xml_data/tmp_s124.xml").read()
    result_list = os.listdir(result_path)
    geojson = ''
    for f in result_list:
        if splitext(f)[1] == '.geojson':
            fullpath = result_path + f
            geojson = open(fullpath).read()
    print(geojson)


    # if (num >= 5):
    #     break
    if commit_count %10 ==0:
        print("============================================================================")
        print("COMMIT   DATA")
        conn.commit()

    commit_count +=1
conn.commit()
cursor1.close()
cursor.close()
conn.close()
