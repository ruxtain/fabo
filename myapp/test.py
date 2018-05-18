from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from .views import *
from .models import *

# 测试是否能够正常登录

class ClientTest(TestCase):
    '''
    模拟浏览器的基本行为。注意，由于test不会去触碰真正的数据库，而是自己造一个临时的，并且在测试完成后摧毁。
    所以要模拟登录的话，需要在这个临时数据库里造一个用户。
    '''
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = User.objects.create_user('michael', 'ruxtain@yeah.net', 'tan.1993')
        self.user.save()

    # def test_login(self):
    #     '''测试我的boss账号能否登录。'''
    #     response = self.client.post('/login/', {'username':'michael', 'password':'tan.1993'})
    #     user = authenticate(username='michael', password='tan.1993')
    #     r=user.is_login()
    #     self.assertEqual(r, True)


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='michael', email='ruxtain@yeah.net', password='tan.1993')
        self.user.profile = Profile(nickname="testman") 
        self.user.profile.save()
        self.user.save()

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get('/login')

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        # request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = profilePage(request, 'michael')
        # Use this syntax for class-based views.
        print(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)



























