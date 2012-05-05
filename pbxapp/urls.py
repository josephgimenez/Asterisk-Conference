from django.conf.urls.defaults import *
from pbxapp.confapp import views

urlpatterns = patterns('',
    (r'^conf/$', views.conference),
    (r'^$', views.home),
    (r'^phones/$', views.phones)
)
