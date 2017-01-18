from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pvp$', views.pvp, name='pvp'),
    url(r'^getpicture$', views.getpicture, name='getpicture'),
    url(r'^getpvppicture$', views.getpvppicture, name='getpvppicture'),
    url(r'^sendtranscript$', views.sendtranscript, name='sendtranscript'),
    url(r'^sendpvptranscript$', views.sendpvptranscript, name='sendpvptranscript'),
    url(r'^hiscores$', views.hiscores, name='hiscores'),
    url(r'^wordresults$', views.wordresults, name='wordresults'),
]
