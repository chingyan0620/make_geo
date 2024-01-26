import torch.nn as nn
import torch
import codecs

class Slotfilling(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers, output_dim, dropout=0.2):
        super(Slotfilling, self).__init__()

        self.word_embed = nn.Embedding(num_embeddings=vocab_size,
                                       embedding_dim=embed_size,
                                       padding_idx=0)

        self.encoder = nn.LSTM(input_size=embed_size,
                               hidden_size=hidden_size,
                               num_layers=num_layers,
                               dropout=dropout,
                               batch_first=True,
                               bidirectional=True)

        self.linear = nn.Linear(2*hidden_size, output_dim)
        self.log_softmax = nn.LogSoftmax(dim=-1)

    def forward(self, seq, input_length=False):
        '''
        :param seq: Tensor Variable: [batch_size, max_seq_len], tensor for sequence id
        :param input_length: list[int]: list of sequences lengths of each sequence
        :return:
        '''

        '''Embedding Layer'''
        # [batch, max_seq_len, embed_size]
        embedding = self.word_embed(seq)
        if input_length:
            input_lstm = nn.utils.rnn.pack_padded_sequence(
                input=embedding, lengths=input_length, batch_first=True)
        else:
            input_lstm = embedding

        ''''LSTM Layer'''
        # [batch, max_seq_len, 2*hidden_size]
        output, _ = self.encoder(input_lstm)

        if input_length:
            output, _ = nn.utils.rnn.pad_packed_sequence(
                output, batch_first=True)

        '''Prediction Layer'''
        Log_prob_predict = self.log_softmax(self.linear(output))
        return Log_prob_predict  # [batch, max_seq_len, trg_vocab_size]
    
class Seq_Dictionary():
    def __init__(self, filepath):
        self.word2idx = dict()
        self.idx2word = dict()
        self.label2idx = dict()
        self.idx2label = dict()
        self.makedict(filepath)
        # self.makedict(data)

    def makedict(self, filepath):
        self.word2idx['<PAD>'] = 0
        self.word2idx['<UNK>'] = 1
        self.idx2word[0] = '<PAD>'
        self.idx2word[1] = '<UNK>'
        self.label2idx['<PAD>'] = 0
        self.label2idx['<UNK>'] = 1
        self.idx2label[0] = '<PAD>'
        self.idx2label[1] = '<UNK>'

        with codecs.open(filepath, encoding='utf-8', mode='r') as f:
        # lines = f.readlines()
        # with codecs.open("./ml_process/test.txt", encoding='utf-8', mode='r') as f:
            lines = f.readlines()
            for line in lines:
            # for line in dates:
                if line.strip() != '':
                    word, label = line.strip().split()
                    if word not in self.word2idx:
                        self.word2idx[word] = len(self.word2idx)
                        self.idx2word[len(self.idx2word)] = word
                    if label not in self.label2idx:
                        self.label2idx[label] = len(self.label2idx)
                        self.idx2label[len(self.idx2label)] = label
    
    def get_word_idx(self, word):
        if word not in self.word2idx:
            return self.word2idx['<UNK>']
        return self.word2idx[word]

    def get_label_idx(self, label):
        if label not in self.label2idx:
            return self.label2idx['<UNK>']
        return self.label2idx[label]

    def get_label_word(self, idx):
        if idx > len(self.idx2label)-1:
            return '<UNK>'
        return self.idx2label[idx]

    def get_word_word(self, idx):
        if idx > len(self.idx2word)-1:
            return '<UNK>'
        return self.idx2word[idx]

class data_prcess():
    def __init__(self, datas):
        self.datas = datas
    def get_file_msg(self):
        # fname = filepath.split('/')[-1]
        # with codecs.open(filepath, 'r') as rf:
        # content = rf.readlines()
        i, msg_list, tmp_list = 0, [], []
        
        for line in self.datas:
            if not line.strip().startswith('-') and line.strip() != '':
                if line.strip().split()[0] != 'NNNN':
                    [tmp_list.append(word)
                        for word in line.strip().split()]
                else:
                    [tmp_list.append(word)
                        for word in line.strip().split()]
                    # if not self.getBrokefile(tmp_list, fname):
                    #     msg_list.append(self.data_cleaning(tmp_list))
                    i += 1
                    tmp_list = []
        return msg_list
    
    def predict( raw_seq, lstm_model, seq_dict):
        # if os.path.exists(savepath):
        #     os.remove(savepath)
        num = 0
        for seq in raw_seq:
            output_label = []
            tensor_seq = torch.LongTensor(1, len(seq)).zero_()
            for i in range(len(seq)):
                tensor_seq[0, i] = seq_dict.get_word_idx(seq[i])
            
            predict_out = lstm_model(tensor_seq)
            labels = torch.topk(predict_out, 1, dim=-1)
            output_label.append([seq_dict.get_label_word(i)
                                for i in labels[1].squeeze().data.cpu().numpy()])
            # print(seq)
            # print(output_label)

            res = []
            for word, predict_label in zip(seq, output_label[0]):
                res.append([word , predict_label])
            return res    

            
            # with codecs.open(savepath, encoding='utf-8', mode='a') as pf:
            #     for word, predict_label in zip(seq, output_label[0]):
            #         pf.write('{}\t{}\n'.format(word, predict_label))
            #     pf.write('\n')
            #     num += 1
            #     print('Finish {}/{} message.'.format(num, len(raw_seq)))

