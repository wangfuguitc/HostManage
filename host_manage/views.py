from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.shortcuts import render
from django import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from host_manage import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.hashers import make_password, check_password


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})
    password = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})


class Login(View):
    next_url = '/'

    def get(self, request):
        Login.next_url = request.GET.get('next', '/')
        return render(request, 'login.html')

    def post(self, request):
        fm = LoginForm(request.POST)
        error = {}
        if fm.is_valid():
            _username = request.POST.get('username')
            _password = request.POST.get('password')
            user = authenticate(username=_username, password=_password)
            if user:
                login(request, user)
                return redirect(Login.next_url)
            else:
                error['error'] = 'Wrong username or password!'
                return render(request, 'login.html', error)
        return render(request, 'login.html', {'fm': fm})


@method_decorator(login_required(login_url='/login'), 'dispatch')
class Index(View):
    def get(self, request):
        hostgroup = models.HostGroup.objects.all()
        return render(request, 'index.html', {'hostgroup': hostgroup})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('/login')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class Host(View):
    def get(self, request):
        data = {}
        user = models.User.objects.get(username=request.user.username)
        contact_list = user.host.all().order_by('id')
        paginator = Paginator(contact_list, 2)
        page = request.GET.get('page', 1)
        try:
            hosts = paginator.page(page)
        except PageNotAnInteger:
            hosts = paginator.page(1)
        except EmptyPage:
            hosts = paginator.page(paginator.num_pages)
        return render(request, 'host.html', {'hosts': hosts})
    def post(self, request):
        if request.user.get_role_display() == 'admin':
            if request.POST.get('handle') == 'add':
                data={}
                data['host_name'] = request.POST.get('host_name')
                data['state'] = request.POST.get('state')
                data['kind'] = request.POST.get('kind')
                data['group_id'] = models.HostGroup.objects.get(id=request.POST.get('group_id'))
                data['ip'] = request.POST.get('ip')
                data['username'] = request.POST.get('username')
                data['password'] = request.POST.get('password')
                try:
                    host_obj = models.Host.objects.create(**data)
                    user_obj = models.User.objects.get(username=request.user.username)
                    user_obj.host.add(host_obj)
                except:
                    return HttpResponse('添加失败')
        return redirect('/index')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class Hostgroup(View):
    pass


@method_decorator(login_required(login_url='/login'), 'dispatch')
class User(View):
    pass
