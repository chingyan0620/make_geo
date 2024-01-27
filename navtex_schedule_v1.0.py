import  pymysql 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service
import time
from datetime import datetime,timedelta
import get_db

service = Service(executable_path='./geckodriver.exe')
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Firefox(service=service, options=options)
db = get_db.getDB()

conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
cursor = conn.cursor()
cursor.execute("select SHOW_TIME from showtime ORDER BY SHOW_TIME DESC")
dataOne = cursor.fetchone()
format_pattern = '%Y-%m-%d'
if dataOne is None:
    target_date1_str = "2015-01-01"
    target_date1 = datetime.strptime(target_date1_str,format_pattern)
else:
    target_date1_str = str(dataOne[0])[:10]
    target_date1 = datetime.strptime(target_date1_str,format_pattern)

today = datetime.today()
daynum = (today-target_date1).days
date_list = [today - timedelta(days=x) for x in range(daynum)]
date_list.reverse()
ID_content = {}
ID_time = {}
id_num =[]

print(date_list)
for date in date_list:
    # time.sleep(10)
    ID_content = {}
    ID_time = {}
    id_num =[]
    year = datetime.strftime(date,"%Y")
    month = datetime.strftime(date,"%m")
    day = datetime.strftime(date,"%d")
    date_str = datetime.strftime(date ,"%Y-%m-%d")
    # url = "https://keelungradio.wordpress.com/" + year + "/" + month\
        # +"/" + day + "/navtex-message-"+date_str+"/"

    url = "https://keelungradio.wordpress.com/" + year + "/" + month\
        +"/" + day + "/"
    print(url)
    driver.get(url)
    
    # break
    delay = 3 # seconds
    try:
        # get_div = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/article/div")))
        get_div = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/section/div/article/div")))

        
        child_p = get_div.find_elements(By.TAG_NAME,"p")
        print ("Page is ready!")
    except TimeoutException:
        print ("Loading took too much time!")
    # get_div = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/article/div/p")
    
    # item = get_div.text
    content =""
    line_counter = 0 
    triger = 0 
    temp_str = ""
    for item in child_p:
        item = item.text
        temp_str = temp_str + item
        for line in item.splitlines():
            line_counter = line_counter + 1
            if line[:4] == "ZCZC":
                line_counter = 0
                # print("------------------------------------------------------------------")
                id_json = line[-4:]                    
                id_num = id_num + [line[-4:]]
                triger = 1
            if line_counter == 1:

                public_time = line[-4:] +"-"+line[10:13] +"-"+ line[:2]

            if line_counter == 2:
                navtex_id = line[-9:-5] + "." + line[-2:]

            if triger == 1:
                content = content + line+"\n"

            if line == "NNNN":
                triger = 0  
                ID_content.update({navtex_id :[content , public_time]})
                if navtex_id not in ID_time:
                    ID_time.update({navtex_id:[date_str]})
                else:
                    tmpshow = ID_time[navtex_id]
                    if date_str not in tmpshow:
                        tmpshow.append(date_str)
                    
                    ID_time.update({navtex_id:tmpshow})

                content = ""
    with open("content_file/"+date_str+".txt" , "w") as f:
        f.writelines(temp_str)

    id_list = list(ID_content.keys())
    error_text = ""
    cursor.execute("select navtex_s124 from navtex_content")
    have_id = cursor.fetchall()
    
    tmp = []
    for j in have_id:
        tmp.append(j[0])
    
    for k in id_list:
        # print(k)
        check_id = k.split(".")
        if check_id[0].isdigit()!=True or check_id[1].isdigit()!=True:
            text = ""
            text = "ID :"+text + str(k) +"\n"

            text = text + str(ID_content[k][0])
            continue
            # error_report(text)
        # print(tmp)
        if k in tmp:
            # print("break")
            continue

        sql = """INSERT INTO navtex_content(NAVTEX_S124,CONTENT,PUBLICTIME,VER,visible) VALUES (%s, %s, %s,%s,%s)"""
        # try:
        #     a = datetime.strptime(ID_content[k][1],'%Y-%b-%d')
        #     a = a.strftime('%Y-%m-%d')
        #     # print(a)
            
        #     cursor.execute(sql, (k, ID_content[k][0],a,'0','1'))
        # except:
        #     error_text = error_text + "\n" + k + "\n "+  ID_content[k][0] + "\n" +ID_content[k][1] + "\n" 
        #     error_text = error_text +"--------------------------------------------------------"
        
        a = datetime.strptime(ID_content[k][1],'%Y-%b-%d')
        a = a.strftime('%Y-%m-%d')
        cursor.execute(sql, (k, ID_content[k][0],a,'0','1'))
        # error_text = error_text + "\n" + k + "\n "+  ID_content[k][0] + "\n" +ID_content[k][1] + "\n" 
        # error_text = error_text +"--------------------------------------------------------"

    id_list2 = list(ID_time.keys())

    for i in id_list2:
        tmp_list = ID_time[i]
        for j in tmp_list:

            sql = """INSERT INTO showtime(NAVTEX_S124, SHOW_TIME) VALUES (%s, %s)"""
            cursor.execute(sql, (i, j))

conn.commit()
cursor.close()
conn.close()
driver.quit()