from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

import datetime

'''
术语表

Topic 话题，也就是标签
Branch 部门法
Article 具体的法条
'''

class Topic(models.Model):
    '''话题'''
    topic_name = models.CharField(max_length=20) # 设立需要人工审核，所以字数限制不是很重要。
    topic_text = models.CharField(max_length=200) # 表示话题下的那一小段描述性文字。
    topic_icon = models.ImageField(upload_to='myapp/static/myapp/storage/') 
    def __str__(self):
        return self.topic_name

class Profile(models.Model):
    '''
    Customizing your own user is way too complicated and I choose the shortcut,
    use the default user model and add a profile model for it.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDER_CHOICES = (('M', '男'),('F', '女'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="M")      # 要么男要么女，不能隐藏性别。
    nickname = models.CharField(max_length=16, blank=True)  # 知乎：2-8个汉字，4-16个英语字母，用js处理。平时都是显示这个，而全名在个人中心显示，id不显示。
    reg_date = models.DateTimeField("注册时间", auto_now_add=True)    
    avatar = models.ImageField(upload_to='myapp/static/myapp/storage/', blank=True) # 头像，暂时的引用方法：模板的使用方法：{{ user.profile.avatar.url }} 建站后会去购买空间储存
    score = models.IntegerField(default=0) # 暂时不涉及，用户积分
    brief_intro = models.CharField(max_length=40, blank=True) # 一句话介绍，和知乎一样，只能最多40个字符。用于各个地方展示。
    long_intro = models.CharField(max_length=500, blank=True) # 五百字长介绍，仅用于用户个人主页展示。
    location = models.CharField(max_length=20, blank=True) # 推荐写 广东深圳、加州旧金山这样的字样，应该也没谁会写得很长。
    education = models.CharField(max_length=100, blank=True) # 所属大学，我的网站就像facebook，只给大学用！
    topics = models.ManyToManyField(Topic, blank=True) # 关注的话题
    fans = models.ManyToManyField("self", symmetrical=False, blank=True) 
    # 用户可以有粉丝，但是不一定是相互是粉丝，所以symmetrical设置False。文档里讲你是我朋友，我也就是你朋友，symmetrical=True，所以我猜这里是False
    # 值得强调的是，fans本身是profile的field，而不是user的，所以这里的相互关注也是profile之间的，换言之，我的狗和你的狗是朋友，那我们就是朋友。
    def __str__(self):                                                   
        return self.user.username 
    def get_avatar_url(self):
        '''ImageField's default parameter doesn't work, so write a method instead'''
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return 'myapp/static/myapp/img/default.jpg'
    # 补充一点，直接用用户名作为个人主页的后缀。用户名不是隐私（类似百度的账号），而昵称用于对外显示，也不是隐私，只有邮箱是隐私。

class Message(models.Model):
    '''
        还在试验中，初步的构想是两个用户确定一个消息，正如两点确定一条直线那样；两个用户分别是发信人和收信人
        如果不设置 related_name，那么两个 ForeignKey 在数据库的名字一样会发生冲突
    '''
    addresser = models.ForeignKey(Profile, related_name='addresser')
    addressee = models.ForeignKey(Profile, related_name='addressee')
    content = models.TextField(blank=True)
    status = models.BooleanField(default=False) # True 表示已读，否则是未读。
    pub_date = models.DateTimeField('发送日期') # 虽然这个词不太合适，但是懒得整复杂了，一律叫 pub_date
    def __str__(self):
        return self.addresser.user.username + '@' + self.addressee.user.username + ': ' + self.content[:12]

class Branch(models.Model):
    '''现在是部门法'''
    title = models.CharField(max_length=100)
    intro = models.TextField(blank=True) # 法条的解释，一般引用名人的话或者经典的法谚。
    chairman = models.CharField(max_length=5, default="") # 签署主席令的在职国家主席
    source = models.URLField(max_length=200, default="") # 法条来源的网址
    topics = models.ManyToManyField(Topic, blank=True) 
    pub_date = models.DateField('生效时间') # 法条生效的时间
    class Meta:
        ordering = ['-pub_date'] # 按照 pub_date 升序排列 Article 对象。 -pub_date 则是降序。
        # 采用降序排列，这样最新的文章总在前面。
    def __str__(self):
        return self.title

class Article(models.Model):
    '''具体的法条'''
    # num 用于固定每个法条的位置，否则插入一个法条就非常困难。
    num = models.IntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE) # 句子所属的文章。
    article_text = models.TextField("无字数限制", blank=True)
    class Meta:
        ordering = ['num'] # 不再按照pk排序，以免法条改动造成巨大麻烦
    def __str__(self):
        return self.article_text

class Frame(models.Model):
    '''各种的能够赞和踩的东西的父类'''
    user = models.ForeignKey(User) # 不管是何种评论，都有一个评论者。
    text = models.CharField("文本内容", max_length=500)
    pub_date = models.DateTimeField('生成日期', auto_now_add=True)
    class Meta:
        ordering = ['thumb_down'] # 以得赞绝对数排列。1000赞800踩的内容也比1赞0踩的内容有趣，尽管得赞比例小。
        abstract = True # 从此这个 model 不会动数据库，而是起一个创建其他 model 的母板的作用。
    def __str__(self):
        return self.text

class ArticleComment(Frame):
    '''针对法条的评论'''
    vote = models.IntegerField(default=0)
    article = models.ForeignKey(Article, on_delete=models.CASCADE) # 指向法条
    description = models.TextField(default="") # 问题必须有问题描述啊
    publish = models.BooleanField(default=True) # 默认发布，也可以选择私人，这样就相当于记笔记
    class Meta:
        ordering = ['-vote']

# 各种评论汇总
class BranchComment(Frame):
    '''针对部门法的评论'''
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    thumb_up = models.IntegerField('支持数', default=0) # 赞
    thumb_down = models.IntegerField('反对数',default=0) # 踩





