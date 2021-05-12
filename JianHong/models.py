from django.db import models
from django.db.models import CharField, BooleanField, IntegerField, ForeignKey, DateTimeField


class UserInformation(models.Model):
    u_name = CharField(max_length=16)
    u_password = CharField(max_length=128)
    u_email = CharField(max_length=64, unique=True)
    u_isVIP = BooleanField(default=False)
    u_isActivation = BooleanField(default=False)


class Music(models.Model):
    m_name = CharField(max_length=64, unique=True)
    m_file_path = CharField(max_length=512)
    m_isVIP = BooleanField(default=False)
    m_download_number = IntegerField(default=0)
    m_play_number = IntegerField(default=0)


class UserMusic(models.Model):
    um_uid = ForeignKey(UserInformation, on_delete=models.CASCADE)
    um_mid = ForeignKey(Music, on_delete=models.CASCADE)
    um_Favorite = CharField(max_length=256, null=True)


class CacheDB(models.Model):
    key = CharField(max_length=255, primary_key=True)
    val = CharField(max_length=256)
    expire = DateTimeField(null=True)