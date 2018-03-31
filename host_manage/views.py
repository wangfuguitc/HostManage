from django.shortcuts import redirect, HttpResponse
from django.views import View
from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from host_manage import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from host_manage.forms import HostForm, LoginForm, HostGroupForm, UserForm
from django.contrib.auth.hashers import make_password


class Login(View):
    next_url = '/'

    def get(self, request):
        Login.next_url = request.GET.get('next', '/')
        return render(request, 'login.html')

    def post(self, request):
        fm = LoginForm(request.POST)
        error = {}
        # 判断用户名密码格式是否正确
        if fm.is_valid():
            _username = request.POST.get('username')
            _password = request.POST.get('password')
            user = authenticate(username=_username, password=_password)
            # 验证用户名密码是否通过
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
        # 判断是否要通过主机组过滤主机
        if group:
            contact_list = models.Host.objects.filter(group_id=group).order_by('id')
        else:
            contact_list = request.user.host.all().order_by('id')
        # 分页显示主机
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
        # 判断用户是否有管理员权限
        if request.user.get_role_display() == 'admin':
            # 添加主机的操作
            if request.POST.get('handle') == 'add':
                host_form = HostForm(request.POST)
                if host_form.is_valid():
                    obj = host_form.cleaned_data
                    obj['group_id'] = models.HostGroup.objects.get(id=obj['group_id'])
                    host_obj = models.Host.objects.create(**obj)
                    # 用户和主机添加关联
                    request.user.host.add(host_obj)
                    return HttpResponse('ok')
                else:
                    # 添加失败，返回错误信息
                    return HttpResponse(host_form.errors.as_json())
            # 修改主机的操作
            if request.POST.get('handle') == 'modify':
                host_form = HostForm(request.POST)
                if host_form.is_valid():
                    obj = host_form.cleaned_data
                    obj['group_id'] = models.HostGroup.objects.get(id=obj['group_id'])
                    models.Host.objects.filter(id=obj['id']).update(**obj)
                    return HttpResponse('ok')
                else:
                    return HttpResponse(host_form.errors.as_json())
            # 删除主机的操作
            if request.POST.get('handle') == 'delete':
                models.Host.objects.filter(host_name=request.POST.get('host_name')).delete()
                return redirect('/host')
        return redirect('/host')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class HostGroup(View):
    def get(self, request):
        host_group = request.user.host_group.all().order_by('id')
        return render(request, 'host_group.html', {'host_group': host_group})

    def post(self, request):
        # 判断用户是否有管理员权限
        if request.user.get_role_display() == 'admin':
            # 删除操作
            if request.POST.get('handle') == 'delete':
                models.HostGroup.objects.filter(name=request.POST.get('name')).delete()
                return HttpResponse('ok')
            # 修改操作
            if request.POST.get('handle') == 'modify':
                host_group_form = HostGroupForm(request.POST)
                if host_group_form.is_valid():
                    obj = host_group_form.cleaned_data
                    models.HostGroup.objects.filter(id=obj['id']).update(**obj)
                    return HttpResponse('ok')
                else:
                    return HttpResponse(host_group_form.errors['name'])
            # 添加操作
            if request.POST.get('handle') == 'add':
                host_group_form = HostGroupForm(request.POST)
                if host_group_form.is_valid():
                    obj = host_group_form.cleaned_data
                    host_group_obj = models.HostGroup.objects.create(**obj)
                    # 用户和主机组添加关联
                    request.user.host_group.add(host_group_obj)
                    return HttpResponse('ok')
                else:
                    return HttpResponse(host_group_form.errors['name'])
        return redirect('/host_group')


@method_decorator(login_required(login_url='/login'), 'dispatch')
class User(View):
    def get(self, request):
        # 判断是否有管理员权限
        user_id = request.GET.get('id')
        if request.user.get_role_display() == 'admin':
            if user_id:
                if user_id == 'new':
                    user_data = None
                else:
                    user_data = models.User.objects.get(id=user_id)
                host_list = models.Host.objects.all()
                group_list = models.HostGroup.objects.all()
                return render(request, 'user_detail.html',
                              {'host_list': host_list,
                               'group_list': group_list, 'user_id': user_id, 'user_data': user_data})
            else:
                user_list = models.User.objects.all()
                return render(request, 'user.html', {'user_list': user_list})

    def post(self, request):
        # 判断用户是否有管理员权限
        if request.user.get_role_display() == 'admin':
            # 删除操作
            if request.POST.get('handle') == 'delete':
                models.User.objects.filter(id=request.POST.get('id')).delete()
                return HttpResponse('ok')
            user_form = UserForm(request.POST)
            if user_form.is_valid():
                # 添加操作
                if request.POST.get('handle') == 'add':
                    obj = user_form.cleaned_data
                    obj['password'] = make_password(obj['password'])
                    obj_host = []
                    obj_host_group = []
                    if 'host' in obj.keys():
                        obj_host = models.Host.objects.filter(id__in=obj['host'])
                        obj.pop('host')
                    if 'host_group' in obj.keys():
                        obj_host_group = models.HostGroup.objects.filter(id__in=obj['host_group'])
                        obj.pop('host_group')
                    # 添加用户
                    obj_user = models.User.objects.create(**obj)
                    # 给用户添加主机
                    if obj_host:
                        obj_user.host.set(obj_host)
                    # 给用户添加主机组
                    if obj_host_group:
                        obj_user.host_group.set(obj_host_group)
                    return HttpResponse('ok')
                # 修改操作
                if request.POST.get('handle') == 'modify':
                    obj = user_form.cleaned_data
                    if obj['password']:
                        obj['password'] = make_password(obj['password'])
                    else:
                        obj.pop('password')
                    obj_host = []
                    obj_host_group = []
                    if 'host' in obj.keys():
                        obj_host = models.Host.objects.filter(id__in=obj['host'])
                        obj.pop('host')
                    if 'host_group' in obj.keys():
                        obj_host_group = models.HostGroup.objects.filter(id__in=obj['host_group'])
                        obj.pop('host_group')
                    obj_user = models.User.objects.filter(id=obj['id'])
                    obj_user.update(**obj)
                    # 给用户添加主机
                    if obj_host:
                        obj_user.first().host.set(obj_host)
                    # 给用户添加主机组
                    if obj_host_group:
                        obj_user.first().host_group.set(obj_host_group)
            else:
                return HttpResponse(str(user_form.errors))
        return redirect('/user')
