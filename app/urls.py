from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('app.views',
    # /log/
    url(r'^$','show_log'),

    # /log/errors
    url(r'^errors/$','show_error_log'),

    # /log/error/203215
    url(r'^error/(?P<error_id>\d+)/$','show_error_details'),

    # /log/login/
    url(r'^login/$','show_sign_in_page'),

    # /log/debug/
    url(r'^debug/$', 'show_debug'),

    # /log/debugerr/
    url(r'^debugerr/$', 'show_debug_error'),

    # /log/json/domain/
    # /log/json/domain/?days=5
    url(r'^json/domain/$','ajax_getDomainInfo'),

    # /log/json/platform/
    # /log/json/platform/?days=25
	url(r'^json/platform/$', 'ajax_getPlatformInfo'),

    # /log/json/platform/details/
    # /log/json/platform/details/?days=32
	url(r'^json/platform/details/$', 'ajax_getDetailedPlatformInfo'),

    # /log/json/source/
    # /log/json/source/?days=22
	url(r'^json/source/$', 'ajax_getSourceInfo'),

    # /log/json/source/details/
    # /log/json/source/details/?days=15
	url(r'^json/source/details/$', 'ajax_getDetailedSourceInfo'),

    # /log/json/country/
    # /log/json/country/?days=7
    url(r'^json/country/$','ajax_getCountryInfo'),

    # /log/json/details/
    url(r'^json/details/$', 'ajax_getLogDetails'),
	
	# /log/json/errorlist/
	url(r'^json/errorlist/$', 'ajax_getErrorList'),

    # /log/add/
    url(r'^add/$', 'log_event'),

    # /log/add/error/
    url(r'^add/error/$', 'log_error'),
)
