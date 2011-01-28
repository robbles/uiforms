from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.auth.decorators import login_required
from models import UIForm, UIField
import views

uiforms = UIForm.objects.all()
fields = UIField.objects.all()

urlpatterns = patterns('',

    # List of UIForms
    url(r'^$', views.list_uiforms, name='list_uiforms'),

    # Create UIForm
    url(r'^create/$', views.create_uiform, name='create_uiform'),

    # Update UIForm
    url(r'^(?P<slug>[\w-]+)/update/$', views.update_uiform,
        name='update_uiform'),

    # Delete UIForm
    url(r'^(?P<slug>[\w-]+)/delete/$', views.delete_uiform,
        name='delete_uiform'),

    # Preview UIForm
    url(r'^(?P<slug>[\w-]+)/preview/$', views.preview_uiform,
        name='preview_uiform'),

    # Update UIFields
    url(r'^(?P<slug>[\w-]+)/fields/$', views.update_uifields, 
        name='update_uifields'),

    # Check UIForm status
    url(r'^(?P<id>\d+)/status/$', views.status_uiform,
        name='status_uiform'),
)

