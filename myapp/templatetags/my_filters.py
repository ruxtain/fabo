from django import template

import re
import time
import string
from myapp.models import *

register = template.Library()


@register.filter
def get_domain(value):
    '''只要域名，不要 http 头，也不要其他那些小的目录'''
    return re.findall(r"http[s]*://(.*?)/", value)[0]

@register.filter
def index(value, arg):
    return value[int(arg)]

@register.filter
def capitalize(value):
    '''仅用于将文章标题转换成首字母大写'''
    words = value.split()
    words = [word.capitalize() for word in words]
    return ' '.join(words)

@register.filter
def url_adjustment(value):
    '''
    在 models 里，
    avatar = models.ImageField(upload_to='myapp/static/myapp/storage/') 
    在 view 里呈现出来就是：
    <img id="avatar" src="myapp/static/myapp/storage/1.png"/>
    但是根据我测试 {% static 'myapp/img/2.png' %}，得到的 view 是
    src="/static/myapp/2.png"，
    所以我决定手动去掉最前面的 myapp 来实现。
    【注意】该 filter 高度不可移植！
    '''
    return value[5:]


@register.filter
def my_slice(value, length):
    '''
    切割字符串，如果被切割，就有省略号，否则呈现全部内容。
    truncatewords 则是用于切割单词的，和这个很不一样。
    '''

    def char_width(char):
        '''小写字母长度视为1，大写字母1.5，汉字则为2.'''
        if char in string.ascii_lowercase or char in ['-', '_']:
            return 1
        elif char in string.ascii_uppercase:
            return 1.5
        else:
            return 2

    _length = 0
    i = 0
    show = ''
    while _length <= int(length): # 只显示单位长度为length及以下的内容
        try:
            char = value[i]
        except:
            break
        _length += char_width(char)
        show += char
        i += 1

    if value == show:
        return show
    else:
        return show + '...'



@register.filter
def no_html(value):
    '''delete all html stuff'''
    return re.sub(r'<.*?>', '', value)


@register.filter
def merge(sentence_set, max_length):
    '''combine the text of the first few sentences'''
    length = 0
    index = 0
    abstract = ''

    for sentence in sentence_set:
        words = sentence.sentence_text.split()
        for word in words:
            if length < int(max_length):
                abstract += word + ' '
                length += len(word) + 1
            else:
                break
    return abstract


@register.filter
def event_display(value):
    pub_date = value.pub_date.strftime("%m月%d日 %H:%M")
    return '{} 发表 「{}」'.format(pub_date, value.text)


@register.filter
def replace(value):
    '''显示正常的编辑的内容，return, newline 符号等处理'''
    return value.replace("\r", "<br />")

@register.filter
def highlight(value, query):
    '''
        替换指定内容为highlight形式
        例如 value = 'A B C'，query = 'A C'， query.split() = [A, C]

    '''
    for i in query.split():        
        value = value.replace(i, "<span class='highlighted'>" + i + "</span>")
    return value









