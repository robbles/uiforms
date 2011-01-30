from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import login, logout
from django.views.generic.simple import direct_to_template, redirect_to
from staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',

    (r'^accounts/', include('registration.urls')),

    # Include forms app urls
    (r'^forms/', include('forms.urls')),

    # Delegate top-level requests to the forms app
    url(r'^$', 'forms.views.landing_page', name='landing_page'),
)

# Enable admin and staticfiles when in debug mode
if settings.DEBUG:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += patterns(
        (r'^admin/doc/', include('django.contrib.admindocs.urls')),
        (r'^admin/', include(admin.site.urls)),
    )

    urlpatterns += staticfiles_urlpatterns()

