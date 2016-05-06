from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'tutor.views.welcome'),
    url(r'^select_course/$', 'tutor.views.select_course'),
    url(r'^sessions/$', 'tutor.views.sessions'),
    url(r'^sessions/new/$', 'tutor.views.new_session'),
    url(r'^sessions/(?P<session_id>\d+)/$', 'tutor.views.edit_session'),
    url(r'^sessions/(?P<session_id>\d+)/questions/add/$', 'tutor.views.new_question'),
    url(r'^sessions/(?P<session_id>\d+)/questions/edit/(?P<question_id>\d+)/$', 'tutor.views.edit_question'),
    url(r'^sessions/run/(?P<session_id>\d+)/$', 'tutor.views.run_session'),
    url(r'^sessions/api/start_question/$', 'tutor.views.api_start_question'),
    url(r'^sessions/api/get_question_totals/$', 'tutor.views.api_get_question_totals'),
    url(r'^sessions/api/get_number_responding_students/$', 'tutor.views.api_get_number_responding_students'),
    url(r'^sessions/api/get_number_responses/$', 'tutor.views.api_get_number_responses'),
    url(r'^reports/$', 'tutor.views.reports_home'),
    url(r'^reports/session_run_report/$', 'tutor.views.session_run_report'),
    url(r'^reports/api/get_session_runs/$', 'tutor.views.api_report_get_session_runs'),
)
