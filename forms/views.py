import logging
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import create_object, update_object, delete_object
from django.views.generic.list_detail import object_list, object_detail
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from models import UIForm, UIField, UIFormForm, UIFieldForm
log = logging.getLogger(__name__)

@login_required
def landing_page(request):
    # TODO: make actual landing page template
    return redirect('list_uiforms', request.user.username)

@login_required
def list_uiforms(request, username):
    log.debug('list request for %s' % (username))

    check_user(request, username)

    options = {
        'queryset': UIForm.objects.filter(creator__username__exact=username),
        'template_name': 'uiform_list.html',
        'template_object_name': 'uiform',
    }
    return object_list(request, **options)


@login_required
def create_uiform(request, username):
    check_user(request, username)

    if request.method == 'POST':
        # Pre-populate the user from the request
        uiform = UIForm(creator=request.user)
        form = UIFormForm(request.POST, instance=uiform)

        if form.is_valid():
            form.save()
            # Go back to list of UIForms
            return redirect(uiform.get_absolute_url())
    else:
        form = UIFormForm()

    return render_to_response('uiform_create.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@login_required
def update_uiform(request, username, slug):
    log.debug('update request for %s/%s' % (username, slug))

    check_user(request, username)

    uiform = get_object_or_404(UIForm, creator__username__exact=username, slug=slug)

    options = {
        'object_id': uiform.id,
        'form_class': UIFormForm,
        'template_name': 'uiform_update.html',
        'template_object_name': 'uiform',
    }
    return update_object(request, **options)


@login_required
def delete_uiform(request, username, slug):
    log.debug('delete request for %s/%s' % (username, slug))

    check_user(request, username)

    if not UIForm.objects.filter(creator__username__exact=username, slug=slug).count():
        log.warning('Form not found')
        raise Http404('Form %s not found' % slug)

    options = {
        'slug': slug,
        'model': UIForm,
        'template_name': 'uiform_delete.html',
        'template_object_name': 'uiform',
        'post_delete_redirect': reverse('list_uiforms', args=[username]),
    }
    return delete_object(request, **options)

@login_required
def preview_uiform(request, username, slug):
    log.debug('preview request for %s/%s' % (username, slug))

    check_user(request, username)

    options = {
        'slug': slug,
        'queryset': UIForm.objects.filter(creator__username__exact=username),
        'template_name': 'uiform_detail.html',
        'template_object_name': 'uiform',
    }
    return object_detail(request, **options)


@login_required
def create_uifield(request, uiform_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed()

    uiform = get_object_or_404(UIForm, id=uiform_id)

    # Make sure we're adding to a UIForm owned by this user
    check_user(request, uiform.creator.username)

    # Pre-populate the UIForm from the request
    field = UIField(uiform=uiform)
    form = UIFieldForm(request.POST, instance=field)

    if form.is_valid():
        form.save()
        # Go back to list of UIForms
        return redirect(uiform.get_absolute_url())
    else:
        # TODO: render form update page with errors
        return redirect(uiform.get_absolute_url())



def check_user(request, username):
    if request.user.username != username:
        # Return 404 instead of 401 to avoid revealing data
        log.warning('Cross-user request for UIForm')
        raise Http404('UIForm not found')        







