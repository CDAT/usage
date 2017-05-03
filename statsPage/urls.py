from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = patterns('statsPage.views',
    # /
    url(r'^$','show_log'),
    url(r'^help/$','help'),
    url(r'^survey/$','survey'),
    url(r'^platform_bar/$','platform_bar'),
    url(r'^all_years_pie/$','all_years_pie'),
    url(r'^world_stats/$','world_stats'),
    url(r'^geo_stats/$','geo_stats'),
    url(r'^calendar_data/$','calendar_data'),
    url(r'^pie_by_year/$','pie_by_year'),
    url(r'^testing/$','testing'),
    url(r'^bar_sesh/$','bar_sesh'),
    url(r'^most_used_pie/$','most_used_pie'),

    url(r'^k_bro/$','k_bro'),
    url(r'^nested_chart/$','nested_chart'),

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
