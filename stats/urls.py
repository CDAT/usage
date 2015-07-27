from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('stats.views',
    url(r'^session/?$', 'get_session'),

    # /log/add/
    url(r'^add/?$', 'log_event'),

    # /log/add/error/
    url(r'^add/error/?$', 'log_error'),
)
