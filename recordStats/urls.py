from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView

urlpatterns = patterns('recordStats.views',
    # /log/add/
    url(r'^$', 'log_event'),

    # /log/add/error/
    url(r'^error/$', 'log_error'),
)
