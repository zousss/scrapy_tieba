# scrapy_tieba
Crawling data of tieba by scrapy
# 爬取地址:
start_urls = ['http://tieba.baidu.com/f?kw=%E6%A2%A6%E4%B8%89%E5%9B%BD2&ie=utf-8'] 
# 分析页面:
贴吧数据分为主题页，回复页，可以获取到的数据有主题，帖子，帖子回复，以及用户信息。
# 数据库设计：
class UserItem(scrapy.Item):存放用户数据
    user_id,user_name,user_sex,user_vip,user_link,user_fans,user_fork,user_post_age,user_post_num,record_time
class PostItem(scrapy.Item):存放帖子数据
    post_id,topic_id,post_user_id,post_user_name,post_content,post_link,post_floor,post_device,post_time,record_time
class ReplyItem(scrapy.Item):存放帖子回复
    reply_id,reply_post,reply_topic,reply_user_name,reply_content,reply_user_id,reply_time,record_time
class TopicItem(scrapy.Item):存放主题
    topic_id,topic_title,topic_content,topic_author_name,topic_author_id,topic_replies,topic_time,topic_link,record_time
# 爬取过程设计
1.获取每页主题数据
  2.1.获取每个主题每页的帖子数据
    3.获取每个帖子的用户数据
  2.2.获取主题每页帖子回复的数据
  在请求帖子页面时，同时会请求本页的帖子回复数据。
# 遇到的问题
1.开始获取帖子回复数据使用的是xpath从html页面中解析，但是一直取不到数据，原因待查。解决方案：通过chrome分析加载页面时请求的url发现，帖子回复在帖子页面加载的时候从另外一个链接中获取，并且一次性获取到整个页面的回复。
2.暂时只爬取到一部分数据，原因待查。
