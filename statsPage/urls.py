from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('statsPage.views',
    # /
    url(r'^$','show_log'),

    # /errors
    url(r'^errors/$','show_error_log'),

    # /error/203215
    url(r'^error/(?P<error_id>\d+)/$','show_error_details'),

    # /login/
    url(r'^login/$','show_sign_in_page'),

    # /debug/
    url(r'^debug/$', 'show_debug'),

    # /debugerr/
    url(r'^debugerr/$', 'show_debug_error'),
)
