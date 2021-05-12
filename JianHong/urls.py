from django.conf.urls import url
from JianHong import views

urlpatterns = [
    url(r'^hello/', views.hello, name='hello'),

    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^register/', views.register, name='register'),
    url(r'^activation/', views.activation, name='activation'),
    url(r'^sendActivationEmail/', views.sendActivationEmail, name='sendActivationEmail'),
    url(r'^getUserInformation/', views.getUserInformation, name='getUserInformation'),

    url(r'^getMusic/',views.getMusic, name='getMusic'),
    url(r'^getMusicList/',views.getMusicList, name='getMusicList'),

    url(r'^setMusicCollection/', views.setMusicCollection, name='setMusicCollection'),

    url(r'^putMusicToDB/', views.putMusicToDB, name='putMusicToDB'),
    url(r'^putMusicToDir/', views.putMusicToDir, name='putMusicToDir'),

]