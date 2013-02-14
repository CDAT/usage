from django.conf.urls import patterns, include, url
from django.conf import settings
from app.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    # Examples:
    # url(r'^$', 'uvcdat_live.views.home', name='home'),
    ('^visual/$', hello),
    #('^boxfill$', boxfill),
    ('^doutriaux1/log$', showlog),
    ('^(?P<username>.*)/(?P<platform>.*)/(?P<source>uvcdat|cdat|search|bldcnf|bldcmk)/(?P<action>.*)$',insertlog),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
