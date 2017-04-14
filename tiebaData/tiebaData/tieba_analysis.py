# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
#from scrapy.conf import settings
import jieba
import jieba.analyse
import re
import jieba.posseg as pseg
import time

class TiebadataAnalysis(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host = '192.168.112.47',
            db = 'spiderdata',
            user = 'zoujianwei',
            passwd = 'KPhUIEd2t622uwtB1xtZ',
            charset='utf8',
            use_unicode= True,
        )
        self.cursor = self.connect.cursor()
        
    def get_topics(self):
        sql = 'SELECT topic_id,topic_title,topic_content FROM tieba_topic'
        self.cursor.execute(sql)
        topics = self.cursor.fetchall()
        return topics
        
    def get_posts(self,topic):
        sql = 'SELECT post_id,post_content FROM tieba_post where topic_id = %s'
        self.cursor.execute(sql,topic)
        posts = self.cursor.fetchall()
        return posts
        
    def get_replies(self,topic,post):
        sql = 'SELECT reply_content FROM tieba_reply where reply_topic = %s and reply_post = %s' % (topic,post)
        self.cursor.execute(sql)
        replies = self.cursor.fetchall()
        return replies
        
    #调用自带    extract_tags
    def parse(self,content):
        if content:
            tags = jieba.analyse.extract_tags(content, topK=50, withWeight=False, allowPOS=())
            return tags
        else:
            return
            
    #统计词频,并且排序输出
    def parse_freq(self,content):
        words=[]
        stopwords = []
        for word in open("D://Python27//Lib//site-packages//jieba//stop_words.txt", "r"):
            stopwords.append(word.strip())
        if content:
            word_dics = pseg.cut(content,HMM=False)
            words = []
            for w in word_dics:
                words.append(w.word+'_'+w.flag)
        word_freq = {}
        #统计词频，并且去掉停用词
        for word in words:
            if word.strip().encode('utf-8') not in stopwords:
                if word in word_freq:
                    word_freq[word]+=1
                else:
                    word_freq[word]=1
        freq_word = []
        for w, freq in word_freq.items():
                 freq_word.append((w.split('_')[0],w.split('_')[1], freq))
        freq_word.sort(key = lambda x: x[1], reverse = True)
        #freq_word.sort()
        return freq_word
        
    #往词典中添加梦三国相关的词语
    def add_m3g_dic(self,dict_path):
        jieba.load_userdict(dict_path)
        #for dic_word in open(dict_path,'r'):
        #    jieba.add_word(dic_word.split(' ')[0], freq=10000, tag='n')
            
    #写入数据库
    def insert_mysql(self,params):
        sql = 'INSERT INTO tieba_word VALUES(%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.execute(sql,params)
        self.connect.commit()
    
    #获取词语所在的类别
    def get_word_type(self,word):
        sql = "SELECT type FROM m3g_dict WHERE word like '%"+word+"%' group by type"
        self.cursor.execute(sql)
        types = self.cursor.fetchall()
        return types
        
if __name__ == "__main__":
    print '[START TIME:]',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())    
    analysis = TiebadataAnalysis()
    topics = analysis.get_topics()
    dict_path1 = 'D://Python27//Lib//site-packages//jieba//m3g_dict.txt'
    dict_path2 = 'D://Python27//Lib//site-packages//jieba//allGame_dic.txt'
    dict_path3 = 'D://Python27//Lib//site-packages//jieba//negative_dict.txt'
    
    analysis.add_m3g_dic(dict_path1)
    analysis.add_m3g_dic(dict_path2)
    analysis.add_m3g_dic(dict_path3)
    
    #content = '梦三国2的英雄蔡文姬冲击红炎之杖'
    #print '---'.join(jieba.cut(content))
    #分析一个topic的所有帖子和楼层,写进文本。
    for topic in topics:
        posts = analysis.get_posts(topic[0])
        flags = analysis.parse_freq(topic[1]+topic[2])
        for flag in flags:
            #分词结果存入数据库
            if len(flag[0]) > 1:
                param = ['tieba',topic[0],flag[0].encode('utf-8').strip(),int(flag[2]),'topic',flag[1]]
                types = analysis.get_word_type(param[2])
                if len(types):
                    for type in types:
                        params = (param[0],param[1],param[2],param[3],param[4],param[5],type)
                        analysis.insert_mysql(params)
                else:
                    params = (param[0],param[1],param[2],param[3],param[4],param[5],'other')
                    analysis.insert_mysql(params)
                    
        if len(posts):
            #print '[Write topic:]',topic
            file_name = topic[0]+'.txt'
            file_path = 'D://Python27//workSpace//tiebaData//datas//'+file_name
            fo = open(file_path, "w+")
            for post in posts:
                replies = analysis.get_replies(str(topic[0]),str(post[0]))
                #正则替换img图片内容
                post_content = re.sub(r'<(.*?)>','',post[1])
                fo.write(post_content.encode('utf-8')+'\n')
                for reply in replies:
                    #输出到文件中
                    reply_content = re.sub(r'<(.*?)>','',reply[0])
                    fo.write(reply_content.encode('utf-8')+'\n')
            fo.close()
            #获取topk词频的词，写进文本。
            top_file_path = 'D://Python27//workSpace//tiebaData//datas//topK//'+file_name
            content = open(file_path,'rb').read()
            #tags = analysis.parse(content)
            tags = analysis.parse_freq(content)
            if tags:
                topk = open(top_file_path, "w+")
                #topk.write('\n'.join(tags).encode('utf-8'))
                for tag in tags:
                    topk.write(tag[0].encode('utf-8')+':'+str(tag[2])+'\n')
                    #分词结果存入数据库
                    if len(tag[0]) > 1:
                        param = ['tieba',topic[0],tag[0].encode('utf-8').strip(),int(tag[2]),'reply',tag[1]]
                        types = analysis.get_word_type(param[2])
                        if len(types):
                            for type in types:
                                params = (param[0],param[1],param[2],param[3],param[4],param[5],type)
                                analysis.insert_mysql(params)
                        else:
                            params = (param[0],param[1],param[2],param[3],param[4],param[5],'other')
                            analysis.insert_mysql(params)
            else:
                pass
    print '[END TIME:]',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())