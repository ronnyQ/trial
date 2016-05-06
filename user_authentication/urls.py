from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'user_authentication.views.login_form'),
    url(r'^logout/', 'user_authentication.views.do_logout'),
)
