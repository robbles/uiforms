from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django import forms
from django.forms.models import inlineformset_factory
from django.db.models.signals import post_save, post_delete
from datetime import datetime
from uuid import uuid4

class UIForm(models.Model):
    """
    Represents a form created by the user.
    """
    label = models.CharField(max_length=140)
    description = models.TextField()
    creator = models.ForeignKey(User)
    slug = models.SlugField(editable=False)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, **kw):
        # Populate slug field when first saved
        if not self.id:
            self.slug = slugify(self.label)

        super(UIForm, self).save(**kw)

    @models.permalink
    def get_absolute_url(self):
        return ('update_uiform', [self.slug])

    def __unicode__(self):
        return 'URLForm "%s"' % self.label

    def get_preview_form(self, data=None):
        """ Return a form for viewing or processing this UIForm """
        if data:
            return PreviewForm(self, data)
        else:
            return PreviewForm(self)

    def get_field_formset(self, data=None, **kw):
        """ 
        Create and return a FormSet for creating new UIFields.
        """
        UIFieldFormSet = inlineformset_factory(UIForm, UIField, 
                fk_name='uiform', extra=1, formset=BaseUIFieldFormSet)
        if data:
            formset = UIFieldFormSet(data, instance=self)
        else:
            formset = UIFieldFormSet(instance=self)
        return formset


class UIField(models.Model):
    """
    Represents a field in a UIForm.
    """
    field_types = (
        ('B', 'Boolean'),
        ('I', 'Integer'),
    )

    label = models.CharField(max_length=50)
    kind = models.CharField(max_length=1, choices=field_types, default='B')
    description = models.TextField(blank=True)
    uiform = models.ForeignKey(UIForm, editable=False)


def update_field_parent(sender, instance, created=False, **kw):
    """
    Update the timestamp on the parent UIForm when a UIField is saved. 
    """
    uiform = instance.uiform
    uiform.last_updated = datetime.now()
    uiform.save()

post_save.connect(update_field_parent, sender=UIField)
post_delete.connect(update_field_parent, sender=UIField)



class URLToken(models.Model):
    """ 
    Used for generating token URLs for sharing UIForms by email. 
    Note: the token is automatically generated on first save with uuid.uuid4()
    """
    uiform = models.ForeignKey(UIForm, unique=True)
    token = models.CharField(max_length=64, editable=False)

    def save(self, **kw):
        # Populate token field when first saved
        if not self.id:
            self.token = str(uuid4())

        super(URLToken, self).save(**kw)

    @models.permalink
    def get_absolute_url(self):
        """
        Return the token URL for this URLTokens UIForm.
        """
        return ('view_token_uiform', [self.uiform.slug, self.token])

    def __unicode__(self):
        return 'URLToken for "%s" : %s' % (self.uiform.label, self.token)



class UIFormForm(forms.ModelForm):
    """
    The amusingly-named Form for editing and creating UIForms.
    """
    label = forms.CharField(max_length=140, initial='My New UIForm')
    description = forms.CharField(widget=forms.Textarea, 
            initial='A brief description of this form...')

    class Meta:
        model = UIForm
        # User is automatically assigned
        exclude = ('creator',) 

    def clean_label(self):
        """ Checks to make sure labels are unique per user """
        label = self.cleaned_data['label']
        creator = self.instance.creator
        id = getattr(self.instance, 'id', None)
        query = UIForm.objects.filter(label=label, creator=creator)
        if id:
            # Don't count this UIForm as a conflict when updating
            query = query.exclude(id=id)
        if query.count():
            raise forms.ValidationError('You already have a form with this label!')
        return label


class BaseUIFieldFormSet(forms.models.BaseInlineFormSet):
    """
    Formset for adding UIFields inline on the UIForm update page.
    """
    def add_fields(self, form, index):
        super(BaseUIFieldFormSet, self).add_fields(form, index)

        # Don't put a delete checkbox on a create form, that's just silly
        if form.empty_permitted and self.can_delete:
            delete_field = form.fields[forms.formsets.DELETION_FIELD_NAME]
            delete_field.widget = forms.widgets.HiddenInput()


class PreviewForm(forms.Form):
    """ 
    Dynamic form class that builds a custom form from the fields of a
    UIForm and its UIFields.
    """
    def __init__(self, uiform, *args, **kwargs):
        super(PreviewForm, self).__init__(*args, **kwargs)

        # Build the set of fields dynamically from UIFields
        for uifield in uiform.uifield_set.all():
            if uifield.kind == 'B':
                field = forms.BooleanField(label=uifield.label, 
                        help_text=uifield.description)
            elif uifield.kind == 'I':
                field = forms.IntegerField(label=uifield.label, 
                        help_text=uifield.description)
            else: # Ignore unknown fields
                continue
            self.fields['uifield_%d_question' % uifield.id] = field

    def get_results(self):
        """
        Returns a list of {'label':UIField.label, 'answer':the answer} dicts.
        """
        return [{
            'label': self.fields[field].label,
            'answer': self.cleaned_data[field]
        } for field in self.fields]




class ShareForm(forms.Form):
    """
    Form for sharing the address of a UIForm with an email.
    """
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(), required=False)




