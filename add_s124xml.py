import pymysql
import sys
import os
from os.path import isfile, isdir, join, splitext
from nick_code.data_preprocess import data_preprocess
import shapefile
from json import dumps
import json
import pygeoif
from osgeo import ogr,osr
import xml.etree.ElementTree as ET


def get_topic(s124):
    tree = ET.ElementTree(ET.fromstring(xml_text))
    root = tree.getroot()
    prefix_map = {"S100": "http://www.iho.int/s100gml/1.0","xsi":"http://www.w3.org/2001/XMLSchema-instance","S124":"http://www.iho.int/S124/gml/1.0","xlink":"http://www.w3.org/1999/xlink","gml":"http://www.opengis.net/gml/3.2"}

    geo_num = len(root.findall('.//geometry'))
    warning_hazard =root.find('./imember/S124:S124_NWPreamble/title/text',prefix_map).text
    warningNumber = root.find('./imember/S124:S124_NWPreamble/messageSeriesIdentifier/warningNumber',prefix_map).text
    year = root.find('./imember/S124:S124_NWPreamble/messageSeriesIdentifier/year',prefix_map).text
    msg_id = "0" + str(warningNumber)+'.'+str(year)[-2:]
    geomcol =  ogr.Geometry(ogr.wkbMultiPolygon)

    return warning_hazard



import get_db
db = get_db.getDB()
conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
cursor = conn.cursor()
cursor1 = conn.cursor()

cursor1.execute("select DISTINCT(show_time) from showtime order by show_time desc")

all_date = cursor1.fetchall()
target_id_list = []
day_count = 0
for i in all_date:
    # print(i[0])
    sql = "select navtex_s124_id from showtime WHERE show_time =%s"
    cursor1.execute(sql,i)
    id_list = cursor1.fetchall()
    # print(id_list)
    for j in id_list:
        if j[0] not in target_id_list:

            target_id_list.append(j[0])
    day_count+=1
    if day_count >= 10:
        break
# print(target_id_list)

cursor1.execute("select DISTINCT(navtex_s124_id) from geo_table" )
all_geo = cursor1.fetchall()
new =[]
for i in all_geo:
    new.append(i[0])

all_id = []
for i in target_id_list:
    # print(i)
    if i in new:
        continue
    else:
        all_id.append(i)


#---------------   run all
cursor.execute("select navtex_s124_id from navtex_content order by publictime desc")
all_id = cursor.fetchall()

#----------------------------------------------------------


# sql_str = "select navtex_s124_id from showtime WHERE show_time =%s order by navtex_s124_id desc"
# cursor.execute(sql_str,showtime)
# content_id = cursor.fetchall()

# all_id = ['0363.20']
# print(all_geo)
# print(all_id)

# test_count = 0
count = 0
for i in all_id:
    idid = i
    # test_count += 1

    sql_str = "select content from navtex_content WHERE navtex_s124_id =%s"
    cursor.execute(sql_str,i)
    raw_content = cursor.fetchone()[0]
    
    with open("./nick_code/data/raw_data/tmp.txt","w") as f:
        f.writelines(raw_content)
    readpath = "./nick_code/data/raw_data/"
    savepath = "./nick_code/data/data_for_tagging/"
    pre = data_preprocess(readpath, savepath)
    msg = pre.get_file_msg("./nick_code/data/raw_data/tmp.txt")
    
    with open(savepath+"tmp_slip.txt",'w')as d:
        for j in msg:
            for k in j:
                d.write(k+"\n")
                    
    result_path = "./nick_code/data_tmp/"
    result_list = os.listdir(result_path)
    for j in result_list:
        # print(j)
        os.remove(result_path + j)

    shp_path = "./nick_code/data/shapefile/tmp_shp/"
    shp_list = os.listdir(shp_path)
    for j in shp_list:
        os.remove(shp_path + j)
    shp_list1 = os.listdir(shp_path)
    if shp_list1 == []:
        counter = 0
        count += 1
        while(counter < 10):
                
                os.system('python ./nick_code/main_tag.py')
                os.system('python ./nick_code/main_ext.py')
                print(str(i)+" convert ...")
                print("============================================================")
                
                if os.listdir(shp_path) != []:
                    break
                counter += 1
                print(str(i)+"error!! try to rebuilt shp " + str(counter) + " times!")
                if counter == 10:
                    
                    with open("error_log.txt","a") as f1:
                        with open("./nick_code/data/raw_data/tmp.txt",'r')as d:
                            content = d.readlines()
                            f1.writelines(content)
                            f1.write("\n-------------------------------------------------------------")
    xml_text = ""
    with open("./nick_code/data/xml_data/tmp_s124.xml",'r') as file11:
        list_s124 = file11.readlines()
        # print(list_s124)

        for ii in list_s124:
            xml_text = xml_text + str(ii)
        all_s124 = xml_text

    # print(all_s124)
    topic = get_topic(all_s124)
    sql = "INSERT into s124_xml(NAVTEX_S124_ID,S124_XML,TOPIC)VALUES(%s,%s,%s)"
    cursor1.execute(sql,(idid,all_s124,topic))
    conn.commit()
    # ----get shapefile to other type ----#
    shp_list = os.listdir(shp_path)
    for f in shp_list:
        fullpath = shp_path + f
        if isfile(fullpath):
            # print(splitext(f))
            if splitext(f)[1] == '.shp':
                json_full_path = result_path + str(f)[:-4] +".geojson"
                reader = shapefile.Reader(fullpath) 
                fields = reader.fields[1:]
                field_names = [field[0] for field in fields]
                buffer = []
                for sr in reader.shapeRecords():
                    atr = dict(zip(field_names, sr.record))
                    geom = sr.shape.__geo_interface__
                    buffer.append(dict(type="Feature", \
                        geometry=geom, properties=atr)) 
        #------write geojson 
                geojson = open(json_full_path, "w")
                geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
                geojson.close()
                reader.close()
                json_text = open(json_full_path).read()
                json_text1 = json.loads(json_text)
                wkt = json_text1['features'][0]["properties"]["Geometry"]
                
                geom = ogr.CreateGeometryFromWkt(wkt)
                print(geom)
                if geom == None:
                    print("<------------------------------------------------------>")
                    wkt1 = ""
                    geotype = json_text1['features'][0]["geometry"]["type"]

                    poslist = json_text1['features'][0]["geometry"]["coordinates"]

                    
                    if geotype == "POLYGON" or geotype == "Polygon":
                        wkt1 = wkt1 + geotype +"(("
                        for point in poslist[0]:
                            wkt1 = wkt1 +str(point[0]) + str(point[1]) +","
                        wkt1 = wkt1[:-1] + "))"
                    # print(wkt1[:-1])
                    if geotype == "LineString":
                        wkt1 = wkt1 + geotype +"("
                        for point in poslist:
                            wkt1 = wkt1 +str(point[0]) + str(point[1]) +","
                        wkt1 = wkt1[:-1] + ")"
                    print(wkt1)
                else:
                    geom.FlattenTo2D()
                    wkt1 = geom.ExportToWkt()
                name_shp = f.split('.')
                s124_id = "0" + name_shp[1] + "." + name_shp[0]
                # print(wkt1)
                # print(wkt)
                # sql = "INSERT into geo_table(NAVTEX_S124_ID,NUMBER_ID,GEOJSON,WKT)VALUES(%s,%s,%s,ST_GeomFromText(%s))"
                
                
                
    # if test_count >= 5:
    #     cursor1.close()
    #     break
    
    # text = open("./nick_code/data/xml_data/tmp_s124.xml").read()
    # sql = "INSERT into geo_table(GEO_INFORMATION)VALUES(%s)"
    # cursor1.execute(sql,(text))

    result_list = os.listdir(result_path)
    geojson = ''
    for f in result_list:
        if splitext(f)[1] == '.geojson':
            fullpath = result_path + f
            geojson = open(fullpath).read()   

    # if count >= 1:
    #     break
conn.commit()
cursor1.close()
cursor.close()
conn.close()