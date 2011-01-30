from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.list_detail import object_list, object_detail
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.contrib import messages
from uuid import uuid4

import logging
log = logging.getLogger(__name__)

from models import UIForm, UIField, URLToken, UIFormForm, PreviewForm, ShareForm
from utils import *


@login_required
def landing_page(request):
    """
    Just redirect straight to the list of forms, since there's nothing else to
    do in this app :)
    """
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
@result_message(redirect="UIForm created successfully")
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
    if request.method == 'POST':
        # Redirect POSTs to avoid messing with history
        return redirect('preview_uiform', slug)

    options = {
        'slug': slug,
        'queryset': UIForm.objects.filter(
            creator__username__exact=request.user.username),
        'template_name': 'uiform_detail.html',
        'template_object_name': 'uiform',
    }
    return object_detail(request, **options)


def view_token_uiform(request, slug, token):
    # Find the URLToken that matches both the slug and token
    urltoken = get_object_or_404(URLToken, token=token, uiform__slug=slug)
    uiform = urltoken.uiform

    if request.method == 'POST':

        # Visitor has filled out the form
        form = PreviewForm(uiform, request.POST)

        if form.is_valid():
            try:
                send_form_email(request, uiform, form)
                messages.success(request, 'Form submitted! Nice work.')

            except EmailError, e:
                log.error(str(e))
                messages.error(request, 'Error submitting form!')

            return redirect('view_token_uiform', slug, token)
        else:
            messages.error(request, 'Sorry, you need to correct some errors in the form...')
    else:
        # Render a blank form for the visitor to fill out
        form = PreviewForm(uiform)

    return render_to_response('uiform_detail.html', {
        'uiform': uiform,
        'preview_form': form,
    }, context_instance=RequestContext(request))


@login_required
def status_uiform(request, id):
    uiform = get_object_or_404(UIForm, id=id,
            creator__username__exact=request.user.username)
    return render_to_response('uiform.json', {
        'uiform': uiform,
    })
    

@login_required
def share_uiform(request, slug):
    uiform = get_object_or_404(UIForm, slug=slug,
            creator__username__exact=request.user.username)

    if request.method == 'POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            log.debug('Received valid share form, creating token')

            try:
                url = send_share_email(request, uiform, 
                        form.cleaned_data['email'],
                        form.cleaned_data['message'])

                messages.success(request, 'UIForm has been shared at %s' % url)

            except EmailError, e:
                log.error(str(e))
                messages.error(request, 'Error sending email')

            # Go back to UIForm update page
            return redirect('list_uiforms')
    else:
        form = ShareForm()

    return render_to_response('uiform_share.html', {
        'uiform': uiform,
        'form': form,
    }, context_instance=RequestContext(request))




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
            messages.success(request, 'UIFields updated')
            formset.save()

            # Go back to UIForm update page
            return redirect(uiform.get_absolute_url())
    else:
        formset = uiform.get_field_formset()

    return render_to_response('uiform_update.html', {
        'formset': formset,
        'uiform': uiform,
    }, context_instance=RequestContext(request))



