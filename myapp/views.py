from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone

from .models import *

from haystack.query import SearchQuerySet
from haystack.views import SearchView, search_view_factory
import django.views

# 搜索定位是这个网站的灵魂，所以放在最上面
class MySearchView(SearchView):
    '''
        Inherate SearchView. In Django, it uses 'get_context_data' for this functionality.
        But in haystack, we use the old-fashioned 'extra_content'.
    '''
    def extra_context(self, **kwargs):
        context = super(MySearchView, self).extra_context(**kwargs)
        context['logged_in'] = flag
        return context

def search(request): # 控制权从haystack交到我手中了
    sqs = SearchQuerySet().all()
    search_view = search_view_factory(
        view_class=MySearchView,
        template='search/search.html',
        searchqueryset=sqs,
        )
    global flag # 全局，向 extra_context 传参不便，故而用全局变量
    if request.user != AnonymousUser(): # 登录
        flag = True
    else:
        flag = False

    return search_view(request)

def index(request):
    '''首页 - 法条'''
    branches = Branch.objects.all()[:15] # 只展示前 15 篇文章及其第一句话。
    # first_sentences = [article.sentence_set.all()[0] for article in articles]
    # topics = [article.topics.values_list() for article in articles]
    # topics包含的东西大概是这个样子：<QuerySet [(1, '创业', '创业是不容易的。但是我大谭必将成功！')]

    # 通过改变 context 中变量名来改变 template 的父级模板
    # 因为大部分页面内容是相同的，只有顶部的导航栏的显示不同，所以只需要更改父级模板
    # 如果导航栏以下的内容也不同，例如设置资料的页面，那么此时根本不允许无名氏用户进入，而是会跳到登录页面
    # 综上，没有必要对子模板分别设置

    if request.user != AnonymousUser(): # 登录
        context = { 
            'branches': branches, 
            'user': request.user, 
            'logged_in': True, 
        }
    else: # 未登录
        context = { 
            'branches': branches, 
            'logged_in': False,
        }        
    return render(request, 'myapp/index.html', context)

def branch(request, pk):
    '''
        部门法详情页面，法条陈列的页面，核心
    '''
    user = request.user
    branch = Branch.objects.get(pk=pk)
    articles = branch.article_set.all()
    comments = branch.branchcomment_set.all()
    topics = branch.topics.all()
    found_comment = branch.branchcomment_set.filter(user__username=request.user.username) # 检索当前用户是否评论过该文章
    if found_comment: # 意思是找到的文章评论
        can_comment = False
    else:
        can_comment = True
    context = {
        'user': user, 
        'branch': branch, 
        'topics': topics,
        'articles': articles, 
        'comments':comments, 
        'can_comment': can_comment,
    }
    if request.user != AnonymousUser(): # 登录
        context['logged_in'] = True
    else:
        context['logged_in'] = False    
    return render(request, 'myapp/branch.html', context)

@login_required
def article(request, pk):
    '''某个法条的详情页'''
    article = Article.objects.get(pk=pk)
    topics = article.branch.topics.all()
    context = {
        'article': article, 
        'topics': topics,  
    }
    if request.user != AnonymousUser(): # 登录
        context['logged_in'] = True
    else:
        context['logged_in'] = False
    return render(request, 'myapp/article.html', context)


def topics(request):
    '''这个页面用于呈现用户感兴趣的话题的几个最新文章'''
    if request.user != AnonymousUser():
        context = { 
            'user': request.user,
            'logged_in': True,
            }
    else:
        context = {
            'logged_in': False,
        }
    return render(request, 'myapp/topics.html', context)

def topicPage(request, pk):
    '''而这个是用于显示某个具体的话题的N个文章'''
    user = request.user
    topic = Topic.objects.get(pk=pk)
    context = { 'user': user, 'topic': topic }
    return render(request, 'myapp/topicPage.html', context)  

def document(request):
    if request.user != AnonymousUser():
        context = {
            'logged_in': True,
        }
    else:
        context = {
            'logged_in': False,
        }    
    return render(request, 'myapp/document.html', context)

def discover(request):
    if request.user != AnonymousUser():
        context = {
            "logged_in": True,
        }
    else:
        context = {
            'logged_in': False,
        }
    return render(request, 'myapp/discover.html', context)

def signupPage(request):
    '''as the name suggests, it's for signing up'''
    context = {}
    return render(request, 'myapp/signupPage.html', context)

# def signupPage(request):
#     return HttpResponse("不好意思，暂时不开放注册。")



@login_required
def messagePage(request, pk):
    addresser = request.user
    addressee = User.objects.get(pk=int(pk))
    context = {
        'addresser': addresser,
        'addressee': addressee,
    }
    return render(request, 'myapp/messagePage.html', context)


def messageAction(request):
    addressee = User.objects.get(pk=pk)
    return redirect('/message/{}'.format(pk))

    
def signupAction(request):
    '''根据用户提交的表单创建账号，并跳转到用户profile页面'''
    username = request.POST['username']
    password = request.POST['password']
    print(password)
    email = request.POST['email']
    user = User(username=username, password=password, email=email) # all are default fields of django
    user.set_password(password) # use the built-in password maker
    user.save()
    profile = Profile(user=user, nickname=username) # default nickname is the username; use this to attach a profile to the user
    profile.save()
    user = authenticate(username=username, password=password)
    login(request, user)
    return redirect("/profile/{}".format(username))

def loginPage(request):
    if request.GET.get('next') == 'again':
        context = {"error_message": "<span class='red'>您的用户名或者密码有误。请检查后重试。</span>"}
    else:
        context = {}
    return render(request, 'myapp/loginPage.html', context)


def loginAction(request):
    '''
    loginPage是一个页面，等待用户登录，
    登录后，启动这个loginAction，如果登录成功，
    则进入主页，并且那个request还附带user对象。
    Action是没有实际页面的，记住这一点。
    '''
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user) # 在服务器端创建session
        try:
            request.POST['remember'] # if 'remember' is a valid key, it means user clicked '记住我'.
        except:
            request.session.set_expiry(0) # delete session right after close browser
        try: 
            previous_url = request.META["HTTP_REFERER"].split("?next=")[1]
        except IndexError:
            previous_url = "/" # if there's no previous URL, redirect back to <home>
        return redirect(previous_url)
    else:
        return redirect('/login?next=again')

def logoutPage(request):
    '''
    之所以没有加Page这个后缀，是因为这个view只是一个动作，它确实没有呈现出任何页面。
    仅仅是登出并跳转到登录页面。
    '''
    logout(request) # no need to post anything, just the request itself will do the trick
    return redirect('/') # 这里不能写 /login, 因为会死循环
  
@login_required      
def profile(request, username):
    '''
    username 就是被查看个人资料的用户的用户名。
    而 context 里面的 user 则是查看者。
    '''
    user = request.user
    other = User.objects.get(username=username) # 这个是被访问个人中心的那个用户
    profile = other.profile # 被访问者的资料
    try:
        if profile.fans.get(user__username=user.username): # 判断访问者是不是被访问者的粉丝
            is_fan = True 
        else:
            is_fan = False 
    except:
        is_fan = False

    # 这部分处理用户动态。显示动态可以让他的熟人了解他的动向，起到一定制约作用。
    # 此外，不显示他关注了什么谁，也不显示他被谁关注，保护隐私。这是重学习，轻社交的平台。
    
    events = []
    events.extend(list(other.branchcomment_set.all()))        
    events.extend(list(other.articlecomment_set.all()))

    events.sort(reverse=True, key=lambda event:event.pub_date)

    context = { 
        'user': request.user, 
        'profile': profile, 
        'other': other, 
        'is_fan': is_fan,
        'events': events, 
    }
    if request.user != AnonymousUser(): # 登录
        context['logged_in'] = True
    else:
        context['logged_in'] = False     
    return render(request, 'myapp/profile.html', context)

@login_required
def settings(request):
    return render(request, "myapp/settings.html", {'user': request.user, 'logged_in': True})

def accountPage(request):
    return render(request, "myapp/accountPage.html", {'user': request.user})

@login_required
def settingsAction(request):
    user = request.user
    profile = user.profile
    try:
        avatar = request.FILES['avatar'] # 虽然一般都是post，但是图片等文件还是要用FILES。此外，form要加 enctype="multipart/form-data"，这样才能传文件。
        profile.avatar = avatar # 本来profile.avatar就是一个文件对象，所以直接让他等于这个文件对象。
    except MultiValueDictKeyError: # 如果没改变 avatar 就会进入这里
        pass

    # 以下内容就算没有改变，也不会出现MultiValueDictKeyError，因为我的input textarea 里面本身就含有值。

    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.save()

    profile.nickname = request.POST['nickname']
    profile.gender = request.POST['gender']
    profile.status = request.POST['status']
    profile.brief_intro = request.POST['brief_intro']
    profile.long_intro = request.POST['long_intro']
    profile.education = request.POST['education']
    profile.location = request.POST['location']
    profile.save()

    return redirect("/profile/{}".format(user.username))

################################################################
###################### 其他的一些提交动作 #########################
################################################################

def articleCommentAction(request, pk):
    '''文章评论的提交'''
    text = request.POST['comment']
    article = Article.objects.get(pk=pk)
    comment = article.articlecomment_set.create(user=request.user, text=text, pub_date=timezone.now())
    comment.save()
    return redirect('/article/{}'.format(pk))

def questionAction(request, pk):
    '''用于提交提问'''
    text = request.POST['question-title']
    description = request.POST['description']
    sentence = Sentence.objects.get(pk=pk)
    question = sentence.question_set.create(user=request.user, text=text, description=description, pub_date=timezone.now())
    question.save()
    return redirect('/article/{}'.format(pk)) # article 是法条的意思哦


def answerAction(request, pk):
    '''提交回答'''
    question = Question.objects.get(pk=pk)
    text = request.POST['question-text']
    answer = question.answer_set.create(user=request.user, text=text, pub_date=timezone.now())
    answer.save()
    return redirect('/question/{}'.format(pk))



################################################################
###################### 以下内容均为 ajax #########################
################################################################



def signupAjaxAction(request):
    '''注册的时候用于判断是否有重复的用户名或者邮箱'''
    try:
        username = request.POST['username']
        if User.objects.filter(username=username):
            return HttpResponse("false") # 不能注册
        else:
            return HttpResponse("true") # 可以注册
    except:
        email = request.POST['email']
        if User.objects.filter(email=email):
            return HttpResponse("false")
        else:
            return HttpResponse("true")


def followAjaxAction(request):
    '''用于关注和取关'''
    other = User.objects.get(username=request.POST['other'])
    print(other)
    if int(request.POST['follow']) == 1: # 表示我要关注
        other.profile.fans.add(request.user.profile) # 在被访问者的fans'列表'里面加上自己的profile
    else: # 表示要取关
        other.profile.fans.remove(request.user.profile) # 从被访问者那里删除掉自己的profile
    other.save() 
    return HttpResponse("") # 这个return 无意义，但是缺了它会报错


def articleRatingAjaxAction(request):
    '''用于提交对文章的打分'''
    profile = request.user.profile
    score = int(request.POST['score']) # js 里面叫 score，我的 model里面是叫 rating，但是懒得改了。
    article = Article.objects.get(pk=int(request.POST['pk']))
    # 先修改原来的那个 star 对象。如果没有就直接创建一个新的 star。
    stars = Star.objects.filter(profile__pk=profile.pk, article__pk=article.pk)
    if stars:  # 如果存在，首先消除掉之前打分的影响，然后根据新数据重算 article的 rating 。
        # 这个公式的效果就是清除掉这个人原先打的分
        star = stars[0]
        try:
            article.rating = (article.rating * article.rating_count - star.rating) / (article.rating_count - 1)
            article.rating_count -= 1
        except ZeroDivisionError: # 如果之前就一个人打分，想要消除原来的影响，直接清零就实现了
            article.rating = 0
            article.rating_count = 0
        # 从这里开始修改原来的 star
        star.profile = profile
        star.article = article
        star.rating = score
    else: # 不存在则创建，这个会新创建一个 pk，创建好之后就去修改总分
        star = Star(profile=profile, article=article, rating=score)
    
    article.rating = (star.rating + article.rating * article.rating_count) / (article.rating_count + 1)
    article.rating_count += 1
    star.save() # 不仅要保存具体的某次评价，总分数也要保存，所以有两次 save.
    article.save()
    return HttpResponse("谢谢你评价~")

def articleCommentAjaxAction(request):

    '''处理 article detail 页面的评论修改和删除'''

    pk = request.POST['comment_pk']
    article_comment = ArticleComment.objects.get(pk=pk)

    try:
        text = request.POST['new_comment']
        article_comment.text = text
        article_comment.save()
    except:
        pass

    try:
        action = request.POST['action']
        if action == 'del':
            article_comment.delete() # 自己消灭自己
            pass
    except:
        pass
    return HttpResponse("")

def articleCommentAjaxVote(request):

    '''处理用户对文章评论的赞踩'''

    p = request.user.profile
    ac = ArticleComment.objects.get(pk=request.POST['pk'])
    vote = request.POST['vote'] # it's either u or d.
 
    if request.POST['query'] == '1': # query database
        acvs = ArticleCommentVote.objects.filter(profile=p, article_comment=ac)

        if ac.user == p.user: # 不允许给自己投票
            result = 5

        elif acvs: # 存在
            acv = acvs[0] # 取出这个投票对象
            if acv.thumb == True:
                if vote == 'u':
                    result = 1 # voted up, still up.
                elif vote == 'd':
                    result = 2 # voted up, now down.

            elif acv.thumb == False:
                if vote == 'u':
                    result = 3 # voted down, now up.
                elif vote == 'd':
                    result = 4 # voted down, still down.
        else:
            result = 0 # never voted 

    elif request.POST['query'] == '0': # alter database
        result = request.POST['result'] 
        if result == '0':
            acv = ArticleCommentVote(profile=p, article_comment=ac)
            if vote == 'u':
                acv.thumb = True
                ac.thumb_up += 1
            elif vote == 'd':
                acv.thumb = False
                ac.thumb_down += 1
        elif result == '2': # 赞变踩
            acv = ArticleCommentVote.objects.filter(profile=p, article_comment=ac)[0]
            acv.thumb = False
            ac.thumb_up -= 1
            ac.thumb_down += 1
        elif result == '3': # 踩变赞
            acv = ArticleCommentVote.objects.filter(profile=p, article_comment=ac)[0]
            acv.thumb = True
            ac.thumb_up += 1
            ac.thumb_down -= 1
        
        acv.save()
        ac.save()
        result = ""
    return HttpResponse(result)

def questionAjaxVote(request):

    '''
        处理对问题的赞踩
        我需要啰嗦一句。文章评论的赞和踩是分离的，赞归赞，踩归踩，都正常显示出来。
        而问题和回答的赞和踩是混同的。显示的票数是赞与踩的差值。因此得票可能是负数。
        在对回答排序的时候，还是按照点赞数，而不是按照差值。
        我搞不清楚知乎的设计，我这里是参照 stackoverflow 的设计。
    '''

    p = request.user.profile
    q = Question.objects.get(pk=request.POST['pk'])
    vote = request.POST['vote']

    if request.POST['query'] == '1': # query database
        qvs = QuestionVote.objects.filter(profile=p, question=q)

        if q.user == p.user:
            result = 5 # can't vote your own question yo

        elif qvs: # this guy had voted before
            qv = qvs[0]
            if qv.thumb == 1: # he voted up last time
                if vote == "1": 
                    result = 1
                elif vote == "0":
                    result = 2
            elif qv.thumb == 0:
                if vote == "1":
                    result = 3
                elif vote == "0":
                    result = 4

        else:
            result = 0 # never voted 

    elif request.POST['query'] == '0': # alter database, save the vote
        result = request.POST['result'] # retrieve the result according to the previous query
        if result == '0':
            qv = QuestionVote(profile=p, question=q)
            if vote == '1':
                qv.thumb = 1
                q.vote += 1
            elif vote == '0':
                qv.thumb = 0
                q.vote -= 1
        elif result == '1': # click up then up again, it'll cancel the up
            qv = QuestionVote.objects.filter(profile=p, question=q)[0]
            # qv.thumb = 2
            qv.delete()
            q.vote -= 1
            q.save()
            return HttpResponse(result) # delete 之后，就不要去 save 了
        elif result == '2': # up then down
            qv = QuestionVote.objects.filter(profile=p, question=q)[0]
            qv.thumb = 0
            q.vote -= 2
        elif result == '3': # down to up
            qv = QuestionVote.objects.filter(profile=p, question=q)[0]
            qv.thumb = 1
            q.vote += 2
        elif result == '4':
            qv = QuestionVote.objects.filter(profile=p, question=q)[0]
            qv.delete()
            q.vote += 1
            q.save() 
            return HttpResponse(result)           
        q.save()
        qv.save()
        result = ""
    return HttpResponse(result)

def answerAjaxVote(request):

    '''
        运作方式和 questionAjaxVote 一样
    ''' 

    p = request.user.profile
    mark("1")
    print(request.POST['pk'])
    a = Answer.objects.get(pk=request.POST['pk'])
    mark("2")
    vote = request.POST['vote']

    if request.POST['query'] == '1': # query database
        avs = AnswerVote.objects.filter(profile=p, answer=a)

        if a.user == p.user:
            result = 5 # can't vote your own answer

        elif avs: # this guy had voted before
            av = avs[0]
            if av.thumb == 1: # he voted up last time
                if vote == "1": 
                    result = 1
                elif vote == "0":
                    result = 2
            elif av.thumb == 0:
                if vote == "1":
                    result = 3
                elif vote == "0":
                    result = 4
        else:
            result = 0 # never voted 

    elif request.POST['query'] == '0': # alter database, save the vote
        result = request.POST['result'] # retrieve the result according to the previous query
        if result == '0':
            av = AnswerVote(profile=p, answer=a)
            if vote == '1':
                av.thumb = 1
                a.vote += 1
            elif vote == '0':
                av.thumb = 0
                a.vote -= 1
        elif result == '1':
            av = AnswerVote.objects.filter(profile=p, answer=a)[0]
            av.delete()
            a.vote -= 1
            a.save()
            return HttpResponse("")
        elif result == '2': # up then down
            av = AnswerVote.objects.filter(profile=p, answer=a)[0]
            av.thumb = 0
            a.vote -= 2
        elif result == '3': # down then up
            av = AnswerVote.objects.filter(profile=p, answer=a)[0]
            av.thumb = 1
            a.vote += 2
        elif result == '4':
            av = AnswerVote.objects.filter(profile=p, answer=a)[0]
            av.delete()
            a.vote += 1
            a.save()
            return HttpResponse("")
        a.save()
        av.save()
        result = ""
    return HttpResponse(result)

############################
#      编辑内容和删除        #

#  虽然名字是action，其实是 ajax #
############################
#问题修改
def questionEditAction(request):

    pk = request.POST['question_pk']
    question = Question.objects.get(pk=int(pk))

    try:
        delete = request.POST['delete'] # 有这个就可以删除了
        question.delete() # 自爆既视感
    except:
        pass

    try:
        new_question = request.POST['new_question']
        question.text = new_question
        question.save()
    except:
        pass

    try:
        new_description = request.POST['new_description']
        question.description = new_description
        question.save()
    except:
        pass

def answerEditAction(request):
    print("虽然控制台会报错说应该return一个HttpResponse，但是这个错误无影响")
    pk = request.POST['answer_pk']
    new_answer = request.POST['new_answer']
    answer = Answer.objects.get(pk=int(pk))
    answer.text = new_answer
    answer.save()



















    