import pymysql
import get_db , load_model
import toxml_v1_1 

db = get_db.getDB()
conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8',autocommit=True)
cursor = conn.cursor()
cursor.execute("select DISTINCT(show_time) from showtime order by show_time desc")

all_date = cursor.fetchall()
target_id_list = []
day_count = 0
for i in all_date:
    sql = "select navtex_s124 from showtime WHERE show_time =%s"
    cursor.execute(sql,i)
    id_list = cursor.fetchall()
    for j in id_list:
        if j[0] not in target_id_list:
            target_id_list.append(j[0])
    day_count+=1

    if day_count >= 10:
        break

cursor.execute("select DISTINCT(navtex_s124) from geo_table" )
all_geo = cursor.fetchall()
new =[]
for i in all_geo:
    new.append(i[0])

all_id = []
for i in target_id_list:
    if i in new:
        continue
    else:
        all_id.append(i)
print(all_id)
count = 0
for i in all_id:
    # i = "0501.23"
    idid = i
    print("runing : "+str(i))
    sql_str = "select content from navtex_content WHERE navtex_s124 =%s"
    cursor.execute(sql_str,i)
    # raw_content = cursor.fetchone()[0]
    try:
        raw_content = cursor.fetchone()[0]
    except:
        print("error : "+str(i) + "----> cursor error")
        continue
    predict_res = ""
    try:
        predict_res = load_model.ml_parser(raw_content)
    except:
        print("error : "+str(i) + " load model err!!" )
        continue
    try:
        res = toxml_v1_1.build_xml_data(predict_res.predict_res)
    except:
        print("error : "+str(i) + " parse to s124 xml err!!" )
        continue
    topic = " ".join(res.res_dict["subject"])
    sql = "INSERT into s124_xml(NAVTEX_S124,S124_XML,TOPIC,VER)VALUES(%s,%s,%s,%s)"
    cursor.execute(sql,(idid,res.s124,topic,'0'))
    # conn.commit()
    # sql = "INSERT into geo_table(NAVTEX_S124,NUMBER_ID,GEOJSON,WKT,VER)VALUES(%s,%s,%s,ST_GeomFromText(%s),%s)"
    sql = "INSERT into geo_table(NAVTEX_S124,NUMBER_ID,GEOJSON,WKT,VER)VALUES(%s,%s,%s,%s,%s)"
    # print(res.geojson)

    for idx ,geojson in enumerate(res.geojson):
        cursor.execute(sql,(idid,idx,str(geojson),res.geom_list[idx],'0'))
        # conn.commit()
    # break

conn.commit()
cursor.close()
conn.close()