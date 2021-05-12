import os

import requests
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from JianHong.models import *
from JianHong.viewsTool import *


def hello(request):
    return HttpResponse("hello")


# 管理员上传音乐
def putMusicToDB(request):
    path = request.GET.get("path")
    music = {}
    putMusic = {}
    file_path = 'static/music/%s/' % path
    files = os.walk('static/music/%s' % path)

    for root, dirs, file in files:
        for f in file:
            fileName = f.split('.mp3')[0]
            music[fileName] = file_path + f
    for name, file_path in music.items():
        m = Music.objects.values_list("m_name", flat=True)
        if m.exists():
            if name not in m:
                print(name, file_path)
                putMusic[name] = file_path
                m = Music()
                m.m_name = name
                m.m_file_path = file_path
                m.save()
        else:
            print(name, file_path)
            putMusic[name] = file_path
            m = Music()
            m.m_name = name
            m.m_file_path = file_path
            m.save()
    data = {
        "status": 201,
        "msg": "put success",
        "data": putMusic,
    }

    return JsonResponse(data=data)


# 根据音乐名获取音乐文件
def getMusic(request):
    music_name = request.GET.get("name")
    types = request.GET.get("types")  # play,download

    try:
        music = Music.objects.get(m_name=music_name)
    except Exception:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    music_path = music.m_file_path
    print(music_path)
    music_file = open(music_path, 'rb').read()

    if types:
        if types == "play":
            music.m_play_number += 1
        elif types == "download":
            music.m_download_number += 1
        music.save()

    return HttpResponse(music_file, content_type='audio/mp3')


# 获取音乐列表
def getMusicList(request):
    types = request.GET.get('types')  # byName,byCollection,recommend
    name = request.GET.get('name')

    data = {
        "status": 200,
        "msg": "ok",
    }

    if types == "recommend":
        music = Music.objects.values_list('m_name', flat=True).order_by("?")[:100]
        music_name_list = getList(music)
        data["music"] = music_name_list

    elif types == "byName":
        music = Music.objects.values_list('m_name', flat=True).filter(m_name__contains=name)
        music_name_list = getList(music)
        data["music"] = music_name_list

    elif types == "byCollection":
        uMusic = UserMusic.objects.all().filter(um_uid=request.user)
        musicName_list = []
        for um in uMusic:
            collecte = um.um_Favorite
            collecte_list = eval(collecte)
            if name in collecte_list:  # name: Default(默认收藏), Love(我喜欢)
                musicName_list.append(um.um_mid.m_name)
        data["music"] = musicName_list

    return JsonResponse(data)


# 改变用户歌曲的所属收藏夹
def setMusicCollection(request):
    types = request.GET.get('types')  # add,del
    music_name = request.GET.get('name')
    collection_name = request.GET.get('collection_name')  # name: Default(默认收藏), Love(我喜欢)
    user = request.user

    data = {}

    userMusic = UserMusic.objects.filter(um_uid=user).filter(um_mid__m_name=music_name)
    if userMusic.exists():
        um = userMusic.first()
        favorite = um.um_Favorite
        if favorite:
            favorite = eval(favorite)
        else:
            favorite = []
        if types == "add":
            if collection_name not in favorite:
                favorite.append(collection_name)
                um.um_Favorite = favorite
                um.save()
            data["status"] = 201
            data["msg"] = "add success"

        elif types == "del":
            try:
                favorite.remove(collection_name)
                if len(favorite) <= 0:
                    um.delete()
                else:
                    favorite = str(favorite)
                    um.um_Favorite = favorite
                    um.save()
                data["status"] = 204
                data["msg"] = "del success"
            except ValueError as ex:
                data["status"] = 400
                data['msg'] = "del error"

    else:
        if types == "add":
            music = Music.objects.get(m_name=music_name)
            userMusic = UserMusic()
            userMusic.um_uid = request.user
            userMusic.um_mid_id = music.id
            userMusic.um_Favorite = str([collection_name])
            userMusic.save()
            data["status"] = 201
            data["msg"] = "add success"
        elif types == "del":
            data["status"] = 400
            data['msg'] = "del error"

    return JsonResponse(data=data)


# 登录
@csrf_exempt
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    data = {
        "status": 200,
        "msg": "ok",
    }
    userInformation = UserInformation.objects.filter(u_email=email)
    if userInformation.exists():
        user = userInformation.first()
        dicts = {"username": user.u_name, "email": user.u_email, "isVIP": user.u_isVIP}
        if check_password(password, user.u_password):
            if user.u_isActivation:
                token = uuid.uuid4().hex
                setCache(token, user.id, 60 * 60 * 24)
                data["token"] = token
                data["dicts"] = dicts
            else:
                data["status"] = USER_NOT_ACTIVATED
                data["msg"] = "user not activated"
        else:
            data["status"] = PASSWORD_ERROR
            data["msg"] = "password error"

    else:
        data["status"] = EMAIL_NOT_EXISTS
        data["msg"] = "email_not_exists"

    return JsonResponse(data=data)


# 退出登录
def logout(request):
    data = {
        "status": LOGOUT_SUCCESS,
        "msg": "logout success",
    }
    try:
        token = request.GET.get("token")
        deleteCache(token)
    except Exception:
        pass

    return JsonResponse(data=data)


# 注册
@csrf_exempt
def register(request):
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')

    data = {
        "status": 201,
        "msg": "ok",
    }
    if not username or not email or not password:
        data["status"] = USER_EMAIL_PASSWORD_IS_NULL
        data["msg"] = "user or email or password is null"
        return JsonResponse(data=data)

    print(username, email, password)
    # 对密码进行加密
    password = make_password(password)

    userInformation = UserInformation.objects.all()
    if userInformation.exists():
        for ui in userInformation:
            if ui.u_email == email:
                print("邮箱已存在")
                data["status"] = EMAIL_EXISTS
                data["msg"] = "email exists"
                return JsonResponse(data=data)

    try:
        # 发送邮件
        sentEmail(email, 60 * 5)
    except Exception as ex:
        print(ex)
        data["status"] = EMAIL_SENDING_FAILED
        data["msg"] = "Mail sending failed"
        return JsonResponse(data=data)

    userInformation = UserInformation()
    userInformation.u_name = username
    userInformation.u_email = email
    userInformation.u_password = password
    userInformation.save()

    return JsonResponse(data=data)


# 发送激活邮件
def sendActivationEmail(request):
    email = request.GET.get("email")
    data={
        "status": 200,
        "msg": "ok",
    }
    try:
        # 发送邮件
        sentEmail(email, 60*5)
    except Exception as ex:
        print(ex)
        data["status"] = EMAIL_SENDING_FAILED
        data["msg"] = "Mail sending failed"
    return JsonResponse(data=data)


# 用户激活
def activation(request):
    email = request.GET.get("email")
    token = request.GET.get("token")
    if getCache(email) == token:
        userInformation = UserInformation.objects.get(u_email=email)
        userInformation.u_isActivation = True
        userInformation.save()
    else:
        return HttpResponse("激活链接已过期")

    return HttpResponse("激活成功")


def getUserInformation(request):

    token = request.GET.get("token")
    user_id = getCache(token)
    try:
        ui = UserInformation.objects.get(pk=user_id)
        data = {
            "status": 200,
            "msg": "ok",
            "username": ui.u_name,
            "email": ui.u_email,
            "isVIP": ui.u_isVIP,
            "isActivation": ui.u_isActivation,
        }
    except Exception:
        data = {
            "status": NOT_LOGIN,
            "msg": "not login",
        }

    return JsonResponse(data=data)


def putMusicToDir(request):

    data = {}

    url = request.GET.get("url")
    path = request.GET.get("path")
    music_name = request.GET.get("name")

    if url and path and music_name:
        file_path = 'static/music/%s/%s.mp3' % (path, music_name)
        try:
            r = requests.get(url)
            data["r.status_code"] = r.status_code
            with open(file_path, "wb") as file:
                for f in r.iter_content():
                    file.write(f)
            data["status"] = 200
            data["msg"] = "ok"
        except Exception:
            data["status"] = 400
            data["msg"] = "down error"
    else:
        data["status"] = 403
        data["msg"] = "not have url or path or name"

    return JsonResponse(data=data)