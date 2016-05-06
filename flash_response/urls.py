from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'flash_response.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', include('user_authentication.urls')),
    url(r'^tutor/', include('tutor.urls')),
    url(r'^student/', include('student.urls')),
    url(r'^$', 'main.views.home'),
    # This must be kept last
    url(r'^(?P<session_code>\w+)/$', 'student.views.respond'),
)
