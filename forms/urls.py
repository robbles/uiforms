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

    #TODO: update username regexes on URLs

    # List of UIForms
    url(r'^(?P<username>[\w-]+)/$', views.list_uiforms, name='list_uiforms'),

    # Create UIForm
    url(r'^(?P<username>[\w-]+)/create/$', views.create_uiform, name='create_uiform'),

    # Update UIForm
    url(r'^(?P<username>[\w-]+)/(?P<slug>[\w-]+)/$', views.update_uiform,
        name='update_uiform'),

    # Delete UIForm
    url(r'^(?P<username>[\w-]+)/(?P<slug>[\w-]+)/delete/$', views.delete_uiform,
        name='delete_uiform'),

    # Preview UIForm
    url(r'^(?P<username>[\w-]+)/(?P<slug>[\w-]+)/preview/$', views.preview_uiform,
        name='preview_uiform'),

    # Create UIField for UIForm
    url(r'^(?P<uiform_id>\d+)/fields/create/$', views.create_uifield, name='create_uifield'),
)

