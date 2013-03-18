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
    # /log/json/domain/?days=5
    url(r'^json/domain/.*','ajax_getDomainInfo'),

    # /log/json/platform/
    # /log/json/platform/?days=25
    # (?!regex) == negative lookahead. Only matches if "platform/" is NOT followed by "details"
	url(r'^json/platform/(?!details).*', 'ajax_getPlatformInfo'),

    # /log/json/platform/details/
    # /log/json/platform/details/?days=32
	url(r'^json/platform/details/.*', 'ajax_getDetailedPlatformInfo'),

    # /log/json/source/
    # /log/json/source/?days=22
    # (?!regex) == negative lookahead. Only matches if "source/" is NOT followed by "details"
	url(r'^json/source/(?!details).*', 'ajax_getSourceInfo'),

    # /log/json/source/details/
    # /log/json/source/details/?days=15
	url(r'^json/source/details/.*', 'ajax_getDetailedSourceInfo'),

    # /log/json/country/
    # /log/json/country/?days=7
    url(r'^json/country/.*','ajax_getCountryInfo'),

    # /log/json/details/
    url(r'^json/details/$', 'ajax_getLogDetails'),

    # /log/add/
    url(r'^add/$', 'insertlog'),

    # /log/error/
    url(r'^error/$', 'logError'),
)
