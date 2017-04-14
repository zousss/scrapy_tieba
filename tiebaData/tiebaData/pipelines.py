# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.conf import settings
from tiebaData.items import PostItem,UserItem,TopicItem,ReplyItem

class TiebadataPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode= True,
        )
        self.cursor = self.connect.cursor()
        
    #pipeline默认调用
    def process_item(self, item, spider):
        if item.__class__ == PostItem:
            try:
                sql = 'INSERT INTO tieba_post VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                param = (item['post_id'],item['topic_id'],item['post_user_id'],item['post_user_name'],item['post_content'],item['post_link'],item['post_device'],item['post_floor'],item['post_time'],item['record_time'])
                self.cursor.execute(sql,param)
                self.connect.commit()
            except pymysql.Warning,w:
                print "Warning:%s" % str(w)
            except pymysql.Error, e:
                print "Error:%s" % str(e)
        elif item.__class__ == UserItem:
            try:
                sql = 'INSERT INTO tieba_user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                param = (item['user_id'],item['user_name'],item['user_sex'],item['user_vip'],item['user_link'],item['user_fans'],item['user_fork'],item['user_post_age'],item['user_post_num'],item['record_time'])
                self.cursor.execute(sql,param)
                self.connect.commit()
            except pymysql.Warning,w:
                print "Warning:%s" % str(w)
            except pymysql.Error, e:
                print "Error:%s" % str(e)
        elif item.__class__ == TopicItem:
            try:
                sql = 'INSERT INTO tieba_topic VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                param = (item['topic_id'],item['topic_title'],item['topic_content'],item['topic_author_name'],item['topic_author_id'],item['topic_replies'],item['topic_time'],item['topic_link'],item['record_time'])
                self.cursor.execute(sql,param)
                self.connect.commit()
            except pymysql.Warning,w:
                print "Warning:%s" % str(w)
            except pymysql.Error, e:
                print "Error:%s" % str(e)
        elif item.__class__ == ReplyItem:
            try:
                sql = 'INSERT INTO tieba_reply VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
                param = (item['reply_id'],item['reply_post'],item['reply_topic'],item['reply_user_name'],item['reply_user_id'],item['reply_content'],item['reply_time'],item['record_time'])
                self.cursor.execute(sql,param)
                self.connect.commit()
            except pymysql.Warning,w:
                print "Warning:%s" % str(w)
            except pymysql.Error, e:
                print "Error:%s" % str(e)
        return item