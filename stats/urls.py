from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('stats.views',
    url(r'^session/?$', 'get_session'),
    url(r'^doesthis/?$', 'doesthis'),

    # /log/add/
    url(r'^add/?$', 'log_event'),

    # /log/add/error/
    url(r'^add/error/?$', 'log_error'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
