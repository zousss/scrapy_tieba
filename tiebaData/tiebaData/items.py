# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_sex = scrapy.Field()
    user_vip = scrapy.Field()
    user_link = scrapy.Field()
    user_fans = scrapy.Field()
    user_fork = scrapy.Field()
    user_post_age = scrapy.Field()
    user_post_num = scrapy.Field()
    record_time = scrapy.Field()
 
class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post_id = scrapy.Field()
    topic_id = scrapy.Field()
    post_user_id = scrapy.Field()
    post_user_name = scrapy.Field()
    post_content = scrapy.Field()
    post_link = scrapy.Field()
    post_floor = scrapy.Field()
    post_device = scrapy.Field()
    post_time = scrapy.Field()
    record_time = scrapy.Field()
    
class ReplyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    reply_id = scrapy.Field()
    reply_post = scrapy.Field()
    reply_topic = scrapy.Field()
    reply_user_name = scrapy.Field()
    reply_content = scrapy.Field()
    reply_user_id = scrapy.Field()
    reply_time = scrapy.Field()
    record_time = scrapy.Field()

class TopicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic_id = scrapy.Field()
    topic_title = scrapy.Field()
    topic_content = scrapy.Field()
    topic_author_name = scrapy.Field()
    topic_author_id = scrapy.Field()
    topic_replies = scrapy.Field()
    topic_time = scrapy.Field()
    topic_link = scrapy.Field()
    record_time = scrapy.Field()
