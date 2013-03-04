from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('app.views',
    url(r'^$','show_authentication_page'),
    url(r'^show/$','showlog'),
    url(r'^json/domain/$','ajax_getDomainInfo'),
    url(r'^json/logInfo/$', 'ajax_getLogInfo'),
    url(r'^add/$', 'insertlog'),
)
        
