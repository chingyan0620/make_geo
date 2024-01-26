import torch.nn as nn
import torch
import ml_process.ml_process as model
    
class ml_parser:
    def __init__(self,data_list_obj):
        self.navtex = "test"
        self.data = data_list_obj
        self.data = self.pre_check()
        self.word_embed_size = 512
        self.hidden_size = 256
        self.num_layers = 2
        self.model_path = "./ml_process/lstm_model.model"
        self.orinavtex = "./ml_process/navtex_train.txt"
        self.predict_res = self.load_model()
        
    def pre_check(self):
        res = []
        tmp = ""
        for i in self.data:
            tmp = tmp + i
        tmp = tmp.replace(")" , ")\n")
        return tmp.split("\n")


    def load_model(self):

        seq_dict = model.Seq_Dictionary(self.orinavtex)
        lstm_model_ = model.Slotfilling(len(seq_dict.word2idx), self.word_embed_size,
                                        self.hidden_size, self.num_layers, len(seq_dict.label2idx))
        lstm_model_.load_state_dict(torch.load(self.model_path))
        # if torch.cuda.is_available():
        #     lstm_model_.cuda()
        # predict
        # preprecess = model.data_prcess(self.data)
        preprecess = model.data_prcess(self.data).get_file_msg()

        msg_list, tmp_list = [], []
        for lines in self.data:
            if lines == "":
                continue
            lines = lines.split(" ")
            for line in lines:
                if line.strip() != '':
                    if line.strip() != 'NNNN':
                        tmp_list.append(line.strip())
                    else:
                        tmp_list.append(line.strip())
                        msg_list.append(tmp_list)
                        tmp_list = []
        res = model.data_prcess.predict( msg_list, lstm_model_, seq_dict)
        return res

if __name__ == "__main__":
    import toxml
    import get_db
    import pymysql

    res = ""
    # with open("./test.txt" , "r",encoding="utf-8") as f:
    #     aa = f.readlines()
    #     res = ml_parser(aa)
    db = get_db.getDB()
    conn  =  pymysql.connect(host = db.ip ,user = db.username ,passwd = db.pwd ,db = db.db_name ,port = int(db.port),charset = 'utf8')
    cursor = conn.cursor()
    sql_str = "select content from navtex_content WHERE navtex_s124 =%s"
    cursor.execute(sql_str,'0028.24')
    # cursor.fetchone()[0]
    res = ml_parser(cursor.fetchone()[0])

    print(res.predict_res)
    with open("./test_predict.txt" , 'w') as f:
        for i in res.predict_res:
            for j in i:
                f.write(j + "\t")
            f.write("\n")
    res = toxml.build_xml_data(res.predict_res)
    print(res.res_dict)
