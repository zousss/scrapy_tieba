# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from tiebaData.items import PostItem,UserItem,TopicItem,ReplyItem
import scrapy
import json

import re
import time

#分为主题topic和帖子post。无法显示图片内容
class tiebaSpider(CrawlSpider):
    #用于区别Spider。 该名字必须是唯一的，不可以为不同的Spider设定相同的名字。
    name = "tieba"
    start_urls = ['http://tieba.baidu.com/f?kw=%E6%A2%A6%E4%B8%89%E5%9B%BD2&ie=utf-8']
    baseurl = "http://tieba.baidu.com"
    
    #解析第一页的链接
    def parse(self,response):
        #调用topic分页
        #topic = scrapy.Request(response.url,callback=self.get_topic)
        #yield topic
        topic_page = scrapy.Request(response.url,callback=self.parse_topic_page)
        yield topic_page
        
    #获取主题分页链接
    def parse_topic_page(self, response):
        #http://tieba.baidu.com/f?kw=%E6%A2%A6%E4%B8%89%E5%9B%BD2&ie=utf-8&pn=17750
        print '*********************%s************************' % response.url
        last_pagination_item = response.xpath('//div[@class = "thread_list_bottom clearfix"]/div[@id = "frs_list_pager"]/a[@class="last pagination-item "]/@href').extract()
        max_page = re.search(r'.*pn=(\d+)',last_pagination_item[0]).group(1) if last_pagination_item else '1'
        for i in range(int(max_page)/50+1):
            link = 'http://tieba.baidu.com/f?kw=%E6%A2%A6%E4%B8%89%E5%9B%BD2&ie=utf-8&pn='+str(i*50)
            topics = scrapy.Request(link,callback=self.get_topic) if i else scrapy.Request(response.url,callback=self.get_topic)
            yield topics
        
    #获取topic的数据
    def get_topic(self,response):
        print '~~~[GET---TOPIC]~~~'
        #获取当前页所有post链接，传给解析post函数
        for sel in response.xpath('//div[@class="t_con cleafix"]/div[@class="col2_right j_threadlist_li_right "]/div[@class="threadlist_lz clearfix"]/div[@class="threadlist_title pull_left j_th_tit "]/a[@class = "j_th_tit "]/@href').extract():
            url = sel
            link = self.baseurl+url
            post = scrapy.Request(link,callback=self.parse_post_page)
            yield post        
        #获取topic内容
        for sel in response.xpath('//div/ul[@id="thread_list"]/li[@class=" j_thread_list clearfix"]'):
            topic_item = TopicItem()
            topic = sel.xpath('div[@class = "t_con cleafix"]')
            topic_id = re.search(r'\"id\"\:(\d+)\,.*',sel.xpath('@data-field').extract()[0]).group(1)
            topic_replies = topic.xpath('div[@class = "col2_left j_threadlist_li_left"]/span/text()').extract()
            name = topic.xpath('div[@class = "col2_right j_threadlist_li_right "]/div[@class = "threadlist_lz clearfix"]/div[@class = "threadlist_title pull_left j_th_tit "]/a/text()').extract()
            topic_title = name[0] if len(name) else ''
            content = topic.xpath('div[@class = "col2_right j_threadlist_li_right "]/div[@class = "threadlist_detail clearfix"]/div[@class = "threadlist_text pull_left"]/div/text()').extract()
            topic_content = content[0].strip() if len(content) else ''
            author_name = topic.xpath('div[@class = "col2_right j_threadlist_li_right "]/div[@class = "threadlist_lz clearfix"]/div[@class = "threadlist_author pull_right"]/span/@title').extract()
            topic_author_name = re.search(r'.*\:(.*)$',author_name[0]).group(1) if len(author_name) else ''
            author_id = topic.xpath('div[@class = "col2_right j_threadlist_li_right "]/div[@class = "threadlist_lz clearfix"]/div[@class = "threadlist_author pull_right"]/span[@class = "tb_icon_author "]/@data-field').extract()
            topic_author_id = re.search(r'.*\:(\d+)',author_id[0]).group(1) if len(author_id) else ''
            topic_time = topic.xpath('div[@class = "col2_right j_threadlist_li_right "]/div[@class = "threadlist_lz clearfix"]/div[@class = "threadlist_author pull_right"]/span[@class = "pull-right is_show_create_time"]/text()').extract()[0]
            
            topic_item['topic_id'] = topic_id
            topic_item['topic_title'] = topic_title
            topic_item['topic_content'] = topic_content
            topic_item['topic_author_name'] = topic_author_name
            topic_item['topic_author_id'] = topic_author_id
            topic_item['topic_replies'] = topic_replies
            topic_item['topic_time'] = topic_time
            topic_item['topic_link'] = response.url
            topic_item['record_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            yield topic_item
            
    #获取帖子中分页链接
    def parse_post_page(self,response):
        #获取帖子的id
        topic_id = re.search(r'.*\/(\d+)',response.url).group(1)
        #获取帖子回复的页数
        pages = response.xpath('//div[@id="container"]/div[@class="content clearfix"]/div[@class="pb_footer"]/div/div/ul/li/a/@href').extract()
        max_page = ''
        if len(pages):
            max_page = re.search(r'.*pn=(\d+)',pages[-1]).group(1)
            for i in range(1,int(max_page)+1):
                post_page = self.baseurl+'/p/'+topic_id+'?pn='+str(i)
                #解析帖子的内容
                post_ans = scrapy.Request(post_page,callback=self.get_post)
                yield post_ans
                #解析帖子回复的内容https://tieba.baidu.com/p/totalComment?t=1488939548454&tid=3233773608&fid=5711238&pn=1&see_lz=0
                reply_url = 'https://tieba.baidu.com/p/totalComment?t='+str(time.time()).replace('.','')+'&tid='+topic_id+'&fid=5711238&pn='+str(i)+'&see_lz=0'
                replies = scrapy.Request(reply_url,callback=self.get_reply)
                yield replies
                
    #获取帖子内容
    def get_post(self,response):
        print '@@@[GET---POST]@@@'
        post_link = response.url
        topic_id = re.search(r'.*\/(\d+)\?.*',post_link).group(1)
        #获取帖子内容的时候，楼层的回复会在另外一个请求中获取到
        for post in response.xpath('//div[@id="j_p_postlist"]/div[@class="l_post l_post_bright j_l_post clearfix  "]'):
            data_field = post.xpath('@data-field').extract()[0]
            data = json.loads(data_field)
            post_user_name = data['author']['user_name']
            post_user_id = str(data['author']['user_id'])
            post_id = str(data['content']['post_id'])
            post_content = data['content']['content'] if data['content']['content'] else ''
            post_item = PostItem()
            #获取回复的用户主页链接
            user = post.xpath('div[@class="d_author"]/ul[@class="p_author"]/li[@class="d_name"]')
            user_link = self.baseurl+user.xpath('a/@href').extract()[0]
            #请求用户数据
            user = scrapy.Request(user_link,callback=self.get_user)
            user.meta['user_id'] = post_user_id
            yield user
            
            #获取楼层的其它信息
            other = post.xpath('div[@class="d_post_content_main "]/div[@class="core_reply j_lzl_wrapper"]/div[@class="core_reply_tail clearfix"]/div[@class="post-tail-wrap"]')
            post_device = ''
            post_floor = ''
            post_time = ''
            if len(other.xpath('span/text()').extract()) == 4:
                post_device = other.xpath('span[2]/a/text()').extract()[0] if other.xpath('span[2]/a/text()').extract() else '' 
                post_floor = other.xpath('span[3]/text()').extract()[0]  if other.xpath('span[3]/text()').extract() else '' 
                post_time = other.xpath('span[4]/text()').extract()[0]  if other.xpath('span[4]/text()').extract() else '' 
            elif len(other.xpath('span/text()').extract()) == 3:
                post_device = ''
                post_floor = other.xpath('span[2]/text()').extract()[0]  if other.xpath('span[3]/text()').extract() else '' 
                post_time = other.xpath('span[3]/text()').extract()[0]  if other.xpath('span[4]/text()').extract() else '' 
            
            post_item['post_id'] = post_id
            post_item['topic_id'] = topic_id
            post_item['post_user_name'] = post_user_name
            post_item['post_user_id'] = post_user_id
            post_item['post_content'] = post_content
            post_item['post_link'] = post_link
            post_item['post_device'] = post_device
            post_item['post_floor'] = post_floor
            post_item['post_time'] = post_time
            post_item['record_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            yield post_item

    #获取帖子回复的内容
    def get_reply(self,response):
        print '###[GET---REPLY]###'
        comments = json.loads(response.body_as_unicode())['data']['comment_list']
        if len(comments):
            for key in comments.keys():
                comment_infos = comments[key]['comment_info']
                for comment_info in comment_infos:
                    reply_item = ReplyItem()
                    reply_item['reply_id'] = comment_info['comment_id']
                    reply_item['reply_user_name'] = comment_info['username']
                    reply_item['reply_user_id'] = comment_info['user_id']
                    reply_item['reply_time'] = comment_info['now_time']
                    reply_item['reply_content'] = comment_info['content']
                    reply_item['reply_topic'] = comment_info['thread_id']
                    reply_item['reply_post'] = comment_info['post_id']
                    reply_item['record_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    yield reply_item          
                
   #获取用户信息
    def get_user(self,response):
        print '***[GET---USER]***'
        user_item = UserItem()
        user_item['user_id'] = response.meta['user_id']
        user_item['user_link'] = response.url
        vip_info = response.xpath('//div[@id="userinfo_wrap"]/div[@class="userinfo_middle"]/div[@class="userinfo_title"]/span/text()').extract()
        isvip = '0'
        if len(vip_info) == 2:
            isvip = '1'
        user_item['user_vip'] = isvip
        user_item['user_name'] = response.xpath('//div[@id="userinfo_wrap"]/div[@class="userinfo_middle"]/div[@class="userinfo_title"]/div[@class="userinfo-marry"]/@data-username').extract()[0]
        user = response.xpath('//div[@id="userinfo_wrap"]/div[@class="userinfo_middle"]/div[@class="userinfo_num"]/div[@class="userinfo_userdata"]')
        user_sex = user.xpath('span[1]/@class').extract()[0]
        user_post_age = user.xpath('span[2]/text()').extract()[0]
        user_post_num = user.xpath('span[4]/text()').extract()[0]
        other = response.xpath('//div[@id="container"]/div[@class="right_aside"]/div[@class="ihome_aside_section"]/h1[@class="ihome_aside_title"]/span[@class="concern_num"]')
        fans = response.xpath('//div[@id="container"]/div[@class="right_aside"]/div[3]/h1[@class="ihome_aside_title"]/span[@class="concern_num"]/a/text()').extract()
        if len(fans):
            user_item['user_fans'] = fans[0]
        else:
            user_item['user_fans'] = '0'
        forks = other.xpath('a[1]/text()').extract()
        if len(forks):
            user_item['user_fork'] = forks[0]
        else:
            user_item['user_fork'] = '0'
        user_item['user_sex'] = re.search(r'.*userinfo_sex\_(.*)$',user_sex).group(1)
        user_item['user_post_age'] = user_post_age
        user_item['user_post_num'] = user_post_num
        user_item['record_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield user_item