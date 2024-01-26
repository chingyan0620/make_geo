import torch.nn as nn
import torch

import ml_process.ml_process as model
    
class ml_parser:
    def __init__(self,data_list_obj):
        self.navtex = "test"
        self.data = data_list_obj
        self.word_embed_size = 512
        self.hidden_size = 256
        self.num_layers = 2
        self.model_path = "./ml_process/lstm_model.model"
        self.orinavtex = "./ml_process/navtex_train.txt"

    def load_model(self):

        seq_dict = model.Seq_Dictionary(self.orinavtex)
        print(len(seq_dict.word2idx))
        print(len(seq_dict.label2idx))
        lstm_model_ = model.Slotfilling(len(seq_dict.word2idx), self.word_embed_size,
                                        self.hidden_size, self.num_layers, len(seq_dict.label2idx))
        lstm_model_.load_state_dict(torch.load(self.model_path))
        if torch.cuda.is_available():
            lstm_model_.cuda()
        # predict
        # preprecess = model.data_prcess(self.data)
        preprecess = model.data_prcess(self.data).get_file_msg()

        msg_list, tmp_list = [], []
        for lines in self.data:
            lines = lines.split(" ")
            for line in lines:
                if line.strip() != '':
                    if line.strip() != 'NNNN':
                        tmp_list.append(line.strip())
                    else:
                        tmp_list.append(line.strip())
                        msg_list.append(tmp_list)
                        tmp_list = []
        model.data_prcess.predict( msg_list, lstm_model_, seq_dict)

if __name__ == "__main__":
    # print("strart")
    with open("./S124_format_build/test.txt" , "r") as f:
        aa = f.readlines()
        ml_parser(aa).load_model()
