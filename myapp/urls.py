from django.conf.urls import url
from . import views

app_name = 'myapp' # 这个的作用就是增加一个 namespace，从而在template引用时可以 polls: detail。

urlpatterns = [
            url(r'^search/', views.search, name="search"),

            url(r'^$', views.index, name='index'), # 首页
            url(r'^branch/(?P<pk>\d+)$', views.branch, name='branch'),
            url(r'^article/(?P<pk>\d+)$', views.article, name='article'),
            url(r'^signup$', views.signupPage, name='signup'),
            url(r'^signup-action$', views.signupAction, name='signup-action'),
            url(r'^login/$', views.loginPage, name='login'),
            url(r'^login-action/$', views.loginAction, name='login-action'),
            url(r'^logout$', views.logoutPage, name='logout'),
            url(r'^profile/(?P<username>[\w\-_]+)$', views.profile, name='profile'),
            url(r'^settings$', views.settings, name='settings'),
            url(r'^settings-action/$', views.settingsAction, name='settings-action'),
            url(r'^account$', views.accountPage, name='account'), # 改密码、验证邮箱、找回密码等

            #话题页面
            url(r'^topic/(?P<pk>\d+)$', views.topicPage, name='topic'),
            url(r'^topics/$', views.topics, name='topics'),
            url(r'^document/$', views.document, name='document'),
            url(r'^discover/$', views.discover, name='discover'),

            #互动
            url(r'^message/(?P<pk>\d+)$', views.messagePage, name='message'), # 发私信
            url(r'^message-action', views.messageAction, name='message-action'),  # 创建新的私信

            # 提交评论
            url(r'^article-comment-action/(?P<pk>\d+)$', views.articleCommentAction, name='article-comment-action'),
            # 提交问题
            url(r'^question-action/(?P<pk>\d+)$', views.questionAction, name='question-action'),
            # 提交回答
            url(r'^answer-action/(?P<pk>\d+)$', views.answerAction, name='answer-action'),

            #修改问题 以及 问题的描述
            url(r'^question-edit-action', views.questionEditAction, name='question-edit-action'),
            url(r'^answer-edit-action', views.answerEditAction, name='answer-edit-action'),

            # @login_required 使得无权访问的页面跳转到登录页，然后登录后跳会刚刚无权访问的页面
            # http://127.0.0.1:8000/login?next=/article/5


            # 这个是为 ajax 专门写的
            url(r'^signup-ajax-action$', views.signupAjaxAction, name='signup-ajax-action'),
            url(r'^follow-ajax-action$', views.followAjaxAction, name='follow-ajax-action'), # 在profile也没进行关注
            # 用于处理星星
            url(r'^article-rating-ajax-action$', views.articleRatingAjaxAction, name='article-rating-ajax-action'),
            # 用于处理评论者和当前用户一致时，用户对评论的修改
            url(r'^article-comment-ajax-action$', views.articleCommentAjaxAction, name='article-comment-ajax-action'),
            # 处理用户对评论的投票
            url(r'^article-comment-ajax-vote$', views.articleCommentAjaxVote, name='article-comment-ajax-vote'),
            # 处理对问题的投票
            url(r'^question-ajax-vote$', views.questionAjaxVote, name='question-ajax-vote'),
            # 处理对回答的投票
            url(r'^answer-ajax-vote$', views.answerAjaxVote, name='answer-ajax-vote'),
        ]



















