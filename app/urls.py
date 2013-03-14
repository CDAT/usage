from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('app.views',
    url(r'^$','showlog'),
    url(r'^login/$','show_sign_in_page'),
    url(r'^debug/$', 'showdebug'),
    url(r'^debugerr/$', 'showdebugerr'),
    url(r'^json/domain/$','ajax_getDomainInfo'),
    url(r'^json/domain/(?P<_days>\d+)/$','ajax_getDomainInfo'),
	url(r'^json/platform/$', 'ajax_getPlatformInfo'),
	url(r'^json/platform/(?P<_days>\d+)/$', 'ajax_getPlatformInfo'),
    url(r'^json/country/$','ajax_getCountryInfo'),
    url(r'^json/country/(?P<_days>\d+)/$','ajax_getCountryInfo'),
    url(r'^json/details/$', 'ajax_getLogDetails'),
    url(r'^add/$', 'insertlog'),
    url(r'^error/$', 'logError'),
)
