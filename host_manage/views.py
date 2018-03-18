from django.shortcuts import redirect, HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from host_manage import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from host_manage.forms import HostForm, LoginForm, HostGroupForm
from django.contrib.auth.hashers import make_password, check_password


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
        host_form = HostForm()
        return render(request, 'index.html', {'host_form': host_form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('/login')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class Host(View):
    def get(self, request):
        group = request.GET.get('group')
        if group:
            contact_list = request.user.host.filter(group_id=group).order_by('id')
        else:
            contact_list = request.user.host.all().order_by('id')
        paginator = Paginator(contact_list, 2)
        page = request.GET.get('page', 1)
        try:
            hosts = paginator.page(page)
        except PageNotAnInteger:
            hosts = paginator.page(1)
        except EmptyPage:
            hosts = paginator.page(paginator.num_pages)
        return render(request, 'host.html', {'hosts': hosts, 'group': group})

    def post(self, request):
        if request.user.get_role_display() == 'admin':
            if request.POST.get('handle') == 'add':
                host_form = HostForm(request.POST)
                if host_form.is_valid():
                    obj = host_form.cleaned_data
                    obj['group_id'] = models.HostGroup.objects.get(id=obj['group_id'])
                    host_obj = models.Host.objects.create(**obj)
                    request.user.host.add(host_obj)
                    return HttpResponse('ok')
                else:
                    return HttpResponse(host_form.errors.as_json())
            if request.POST.get('handle') == 'modify':
                host_form = HostForm(request.POST)
                if host_form.is_valid():
                    obj = host_form.cleaned_data
                    obj['group_id'] = models.HostGroup.objects.get(id=obj['group_id'])
                    models.Host.objects.filter(id=obj['id']).update(**obj)
                    return HttpResponse('ok')
                else:
                    return HttpResponse(host_form.errors.as_json())
            if request.POST.get('handle') == 'delete':
                models.Host.objects.filter(host_name=request.POST.get('host_name')).delete()
                return redirect('/host')
        return redirect('/index')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class HostGroup(View):
    def get(self, request):
        host_group = request.user.host_group.all().order_by('id')
        return render(request, 'host_group.html', {'host_group': host_group})
    def post(self, request):
        if request.user.get_role_display() == 'admin':
            if request.POST.get('handle') == 'delete':
                models.HostGroup.objects.filter(name=request.POST.get('name')).delete()
                return redirect('/host_group')
            if request.POST.get('handle') == 'modify':
                return redirect('/index')
            if request.POST.get('handle') == 'add':
                host_group_form = HostGroupForm(request.POST)
                if host_group_form.is_valid():
                    obj = host_group_form.cleaned_data
                    host_group_obj = models.HostGroup.objects.create(**obj)
                    request.user.host_group.add(host_group_obj)
                    return HttpResponse('添加成功')
                else:
                    return HttpResponse(host_group_form.errors['name'])
        return redirect('/index')

@method_decorator(login_required(login_url='/login'), 'dispatch')
class User(View):
    pass
