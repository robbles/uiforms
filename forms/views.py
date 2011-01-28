import logging
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.list_detail import object_list, object_detail
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from models import UIForm, UIField, UIFormForm
log = logging.getLogger(__name__)

def register(request):
    pass

@login_required
def landing_page(request):
    # TODO: make actual landing page template
    return redirect('list_uiforms')


###############################################
#
#               UIForms
#
###############################################

@login_required
def list_uiforms(request):
    options = {
        'queryset': UIForm.objects.filter(
            creator__username__exact=request.user.username),
        'template_name': 'uiform_list.html',
        'template_object_name': 'uiform',
    }
    return object_list(request, **options)


@login_required
def create_uiform(request):
    if request.method == 'POST':
        # Pre-populate the user from the request
        uiform = UIForm(creator=request.user)
        form = UIFormForm(request.POST, instance=uiform)

        if form.is_valid():
            form.save()
            # Go to UIForm update page
            return redirect(uiform.get_absolute_url())
    else:
        form = UIFormForm()

    return render_to_response('uiform_create.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def update_uiform(request, slug):
    uiform = get_object_or_404(UIForm, 
            creator__username__exact=request.user.username, slug=slug)

    uifield_formset = uiform.get_field_formset()

    options = {
        'object_id': uiform.id,
        'form_class': UIFormForm,
        'template_name': 'uiform_update.html',
        'template_object_name': 'uiform',
        'extra_context': {
            'formset': uifield_formset,
        },
    }
    return update_object(request, **options)


@login_required
def delete_uiform(request, slug):
    if not UIForm.objects.filter(
            creator__username__exact=request.user.username, slug=slug).count():
        log.warning('Form not found')
        raise Http404('Form %s not found' % slug)

    options = {
        'slug': slug,
        'model': UIForm,
        'template_name': 'uiform_delete.html',
        'template_object_name': 'uiform',
        'post_delete_redirect': reverse('list_uiforms'),
    }
    return delete_object(request, **options)

@login_required
def preview_uiform(request, slug):
    options = {
        'slug': slug,
        'queryset': UIForm.objects.filter(
            creator__username__exact=request.user.username),
        'template_name': 'uiform_detail.html',
        'template_object_name': 'uiform',
    }
    return object_detail(request, **options)


@login_required
def status_uiform(request, id):
    uiform = get_object_or_404(UIForm, id=id,
            creator__username__exact=request.user.username)
    return render_to_response('uiform.json', {
        'uiform': uiform,
    })
    

###############################################
#
#               UIFields
#
###############################################

@login_required
def update_uifields(request, slug):
    uiform = get_object_or_404(UIForm, slug=slug,
            creator__username__exact=request.user.username)

    if request.method == 'POST':
        formset = uiform.get_field_formset(request.POST)
        if formset.is_valid():
            formset.save()

            # Go back to UIForm update page
            return redirect(uiform.get_absolute_url())
    else:
        formset = uiform.get_field_formset()

    return render_to_response('uiform_update.html', {
        'formset': formset,
        'uiform': uiform,
    }, context_instance=RequestContext(request))



def check_user(request, username):
    if request.user.username != username:
        # Return 404 instead of 401 to avoid revealing data
        log.warning('Cross-user request for UIForm')
        raise Http404('UIForm or UIField not found!')        







