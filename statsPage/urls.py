from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = patterns('statsPage.views',
    # /
    url(r'^$','show_log'),
    url(r'^hello_world/$','hello_world'),
    url(r'^sup_world/$','sup_world'),
    url(r'^world_stats/$','world_stats'),
    url(r'^new_stats/$','new_stats'),
    url(r'^calendar_data/$','calendar_data'),

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
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
