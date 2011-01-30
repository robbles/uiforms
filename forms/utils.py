from django.contrib import messages
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings
from models import URLToken

class EmailError(Exception):
    pass

def send_share_email(request, uiform, email, message):
    """
    Sends an email to the given address containing a link to the given UIForm.
    Returns the token URL that was generated.
    """
    # Generate and save a new token if necessary
    token, created = URLToken.objects.get_or_create(uiform=uiform)
    url = request.build_absolute_uri(token.get_absolute_url())

    email_template = get_template('uiform_share_email.txt')
    context = Context({
        'user': request.user,
        'uiform': uiform,
        'url': url,
        'message': message,
    })

    try:
        send_mail('%s has shared a UIForm with you!' % request.user.username, 
                  email_template.render(context),
                  settings.DEFAULT_FROM_EMAIL,
                  [email], fail_silently=False)

    except Exception, e:
        raise EmailError(e)

    return url



def send_form_email(request, uiform, form):
    """
    Sends an email to the creator of a UIForm with the results from someone
    filling it out.
    """
    email_template = get_template('uiform_completed_email.txt')
    context = Context({
        'user': request.user,
        'uiform': uiform,
        'form': form,
    })

    try:
        send_mail('Your UIForm has been completed!', 
                  email_template.render(context),
                  settings.DEFAULT_FROM_EMAIL,
                  [uiform.creator.email], fail_silently=False)
    except Exception, e:
        raise EmailError(e)



def result_message(success=None, failure=None, redirect=None):
    """
    Creates a decorator for a view function that creates a success or failure
    messages depending on the result.

    Assumes that a response with a status_code >= 400 or a thrown exception is
    a failure, and anything else is a success.

    If redirect is passed, log that message instead when 400 > status_code >= 300.
    """
    def decorator(view):
        def wrapper(request, *args, **kw):
            try:
                result = view(request, *args, **kw)
            except Exception, e:
                # Don't mask exception, but report failure first
                messages.error(request, failure)
                raise e

            # There should always be a status_code (if not, we have bigger
            # problems to worry about than messages)
            if hasattr(result, 'status_code'):
                if failure and result.status_code >= 400:
                    messages.error(request, failure)
                elif redirect and result.status_code >= 300:
                    messages.success(request, redirect)
                elif success:
                    messages.success(request, success)

            return result

        return wrapper
    return decorator




