import datetime
import uuid

from django.core.mail import send_mail
from JianHong.models import CacheDB

"""注册"""
# 用户名或邮箱或密码为空
USER_EMAIL_PASSWORD_IS_NULL = 600
# 用户注册的邮箱已存在
EMAIL_EXISTS = 601
# 邮件发送失败
EMAIL_SENDING_FAILED = 602
# 激活链接过期
LINK_EXPIRED = 603

"""登录"""
# 邮箱不存在
EMAIL_NOT_EXISTS = 701
# 密码错误
PASSWORD_ERROR = 702
# 用户未激活
USER_NOT_ACTIVATED = 703
# 用户未登录
NOT_LOGIN = 704
# 退出登录
LOGOUT_SUCCESS = 710

"""获取歌曲"""
# 歌曲已缓存
SONG_CACHED = 801
# 歌曲已下载
SONG_DOWNLOADED = 802

URL = "http://127.0.0.1:8000/jianhong/activation/"


def getList(db):
    list = []
    for d in db:
        list.append(d)
    return list


def sentEmail(email, expire_date):
    token = uuid.uuid4().hex
    url = URL + "?email=%s&token=%s" % (email, token)
    setCache(email, token, expire_date)

    subject = 'JianHongMusic'
    message = "请在5分钟内点击链接,完成激活\n" + url
    from_email = '2230261758@qq.com'
    recipient_list = [email, ]

    # 发送邮件(主机,  邮件内容, 发件人, 收件人列表)
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)


def flushCache():
    cacheDB = CacheDB.objects.all()
    if cacheDB.exists():
        for c in cacheDB:
            if c.expire < datetime.datetime.now():
                cacheDB.delete()


def deleteCache(key):
    cacheDB = CacheDB.objects.get(key=key)
    cacheDB.delete()


def setCache(key, val, expire):
    flushCache()
    expire_data = datetime.datetime.now() + datetime.timedelta(seconds=expire)
    cacheDB = CacheDB.objects.filter(key=key)
    if cacheDB.exists():
        cacheDB.delete()
    cacheDB = CacheDB()
    cacheDB.key = key
    cacheDB.val = val
    cacheDB.expire = expire_data
    cacheDB.save()


def getCache(key):
    cacheDB = CacheDB.objects.filter(key=key)
    if cacheDB.exists():
        if cacheDB.first().expire > datetime.datetime.now():
            return cacheDB.first().val
        else:
            flushCache()
            return None
    else:
        return None
