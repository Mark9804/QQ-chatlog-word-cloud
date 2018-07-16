import re
import os
import jieba as jb
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from scipy.misc import imread
from pylab import mpl

message_re = "(201\d-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (.*)[\(,<](.+)[\),>]\n(.*)(?=\n\n)"
#r可以不要把
#(201\d-\d{2}-\d{2})日期 
#(\d{2}:\d{2}:\d{2})时间 
#名字(.*)
#[\(,<](.+)[\),>] QQ号或者QQ邮箱
#\n(.*)(?=\n\n) 消息内容，观察聊天记录文件发现每个消息内容后有两个换行符
message_compile = re.compile( message_re )
mpl.rcParams['font.sans-serif'] = ['SimHei']
#plt.title()需要的字体

def read(name):
    word_data = {}
    with open('chatlog.txt', encoding = 'utf-8') as chat:

        message_data = message_compile.findall(chat.read())
        #findall针对group返回一个嵌套了元祖的列表
        for item in message_data:
            #item[0]=date, item[1]=time, item[2]=name, item[3]=QQ, item[4]=message
            if not word_data.get(item[3]):
                word_data[item[3]] = {'name' : item[2], 'message' : list(jb.cut(item[4]))}
                #字典中嵌套字典
                #第一层的字典的key是QQ号，value是一个包括名字和消息的字典
            else:
                word_data[item[3]]['name'] = item[2]
                #如果已经有这个QQ号了，那么更新他的群名片
                word_data[item[3]]['message'] += list(jb.cut(item[4])) #对列表的+=和append()一样
    #with open('第一次read以后的字典.txt','a',encoding = 'utf-8') as f:
    #    for qq in list(word_data.keys()):
    #        f.writelines(str(word_data[qq]['name'])+'\n')
    #        f.writelines(str(word_data[qq]['message'])+'\n')
    return word_data

def delete(data):
    with open('stopwords.txt', encoding = 'utf-8') as file: #决定一下自己以后打代码用file还是f还是..
        stopword = file.read().split('\n')
        #read()得到一个列表
        #split('\n')根据换行符分割列表
        for item in list(data.keys()):
            data[item]['message'] = Counter(data[item]['message'])
            #会把'message'这个键的值（是个列表）生成为键为单词，值为出现次数的字典
            for word in list(data[item]['message'].keys()):
                #用list()可以避免什么问题？
                #要对字典进行操作的话不能用字典.keys()作索引，因为字典内容会变，必须用list取一个原始的拷贝
                if word in stopword:
                    del(data[item]['message'][word])
    #with open('第二次delete以后的字典.txt','a',encoding = 'utf-8') as f:
    #    for qq in list(data.keys()):
    #        f.writelines(str(data[qq]['name'])+'\n')
    #        f.writelines(str(data[qq]['message'])+'\n')
    return data
#data是一个三层嵌套，第一层key = QQ号，第二层key有QQ名和message，message下有第三层是单词和频次
def draw(name, message_counter, token):
    #token记录成功进入if not分支的次数
    wc = WordCloud(
        font_path = 'msyh.ttc',
        max_words = 100,
        background_color = 'white',
        mask = imread('mask.png')
    )
    word_dict = {}
    for item in list(message_counter.keys()):
        if message_counter[item] >= 5:
            word_dict[item] = message_counter[item]
    #print(word_dict)

    #with open('message_counter.txt', 'a', encoding='utf-8') as f:
    #    f.writelines(name+'\n')
    #    f.writelines(str(word_dict)+'\n')
    for item in list(word_dict.keys()):
        if item.isdigit():
            del word_dict[item]
    if  word_dict:
        #有人发言的词汇的最大频数不超过5次！，不能传入空字典给wordcloud绘图
        token += 1
        print('进入if not分支，还未绘图，token = ' + str(token))
        word_cloud_pic = wc.generate_from_frequencies(word_dict)
        print('绘图成功')
        plt.imshow(word_cloud_pic)
        plt.title(name)
        plt.axis('off')
        plt.savefig('图片\\'+name+'.png', dpi=400)
     
if __name__ == '__main__':
    message_data = read('chatlog')
    message_data = delete(message_data)
    token = 0
    for qq in message_data.keys():
        draw(message_data[qq]['name'], message_data[qq]['message'], token)


            