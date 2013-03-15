from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('app.views',
    # /log/
    url(r'^$','showlog'),

    # /log/login/
    url(r'^login/$','show_sign_in_page'),

    # /log/debug/
    url(r'^debug/$', 'showdebug'),

    # /log/debugerr/
    url(r'^debugerr/$', 'showdebugerr'),

    # /log/json/domain/
    url(r'^json/domain/$','ajax_getDomainInfo'),

    # /log/json/domain/3/
    url(r'^json/domain/(?P<_days>\d+)/$','ajax_getDomainInfo'),

    # /log/json/platform/
	url(r'^json/platform/$', 'ajax_getPlatformInfo'),

    # /log/json/platform/25/
	url(r'^json/platform/(?P<_days>\d+)/$', 'ajax_getPlatformInfo'),

    # /log/json/platform/details/
	url(r'^json/platform/details/$', 'ajax_getDetailedPlatformInfo'),

    # /log/json/platform/32/details/
	url(r'^json/platform/(?P<_days>\d+)/details/$', 'ajax_getDetailedPlatformInfo'),

    # /log/json/source/
	url(r'^json/source/$', 'ajax_getSourceInfo'),

    # /log/json/source/22/
	url(r'^json/source/(?P<_days>\d+)/$', 'ajax_getSourceInfo'),

    # /log/json/source/details/
	url(r'^json/source/details/$', 'ajax_getSourceDetailedInfo'),

    # /log/json/source/15/details/
	url(r'^json/source/(?P<_days>\d+)/details/$', 'ajax_getSourceDetailedInfo'),

    # /log/json/country/
    url(r'^json/country/$','ajax_getCountryInfo'),

    # /log/json/country/7/
    url(r'^json/country/(?P<_days>\d+)/$','ajax_getCountryInfo'),

    # /log/json/details/
    url(r'^json/details/$', 'ajax_getLogDetails'),

    # /log/add/
    url(r'^add/$', 'insertlog'),

    # /log/error/
    url(r'^error/$', 'logError'),
)
