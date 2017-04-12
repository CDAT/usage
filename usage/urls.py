from django.views.generic.base import RedirectView
from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'log/', include('stats.urls')),
    url(r'login/', include('login.urls')),
    (r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'^$', RedirectView.as_view(url='/stats/')),
    # url(r'^', include('statsPage.urls')), # match everything else...
    url(r'^stats/', include('statsPage.urls')), # match everything else...
    # url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/stats'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
