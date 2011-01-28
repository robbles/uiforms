from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django import forms
from django.forms.models import inlineformset_factory
from django.db.models.signals import post_save
from datetime import datetime
import logging
log = logging.getLogger(__name__)

class UIForm(models.Model):
    label = models.CharField(max_length=140)
    description = models.TextField()
    creator = models.ForeignKey(User)
    slug = models.SlugField(editable=False)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, **kw):
        # Populate slug field when saved
        self.slug = slugify(self.label)
        super(UIForm, self).save(**kw)

    @models.permalink
    def get_absolute_url(self):
        return ('update_uiform', [self.slug])

    def get_field_formset(self, data=None, **kw):
        """ 
        Create and return a FormSet for creating new UIFields.
        """
        log.debug('Fetching UIField formset for UIForm %s' % self.slug)
        UIFieldFormSet = inlineformset_factory(UIForm, UIField, 
                fk_name='uiform', extra=1, formset=BaseUIFieldFormSet)
        if data:
            formset = UIFieldFormSet(data, instance=self)
        else:
            formset = UIFieldFormSet(instance=self)
        return formset

    def get_update_form(self):
        """ Create and return a form for updating this UIForm """
        return UIFormForm(self)

    def get_preview_form(self):
        """ Create and return a form for previewing this UIForm """
        return PreviewForm(self)



class UIField(models.Model):
    field_types = (
        ('B', 'Boolean'),
        ('I', 'Integer'),
    )

    label = models.CharField(max_length=50)
    kind = models.CharField(max_length=1, choices=field_types, default='B')
    description = models.TextField(blank=True)
    uiform = models.ForeignKey(UIForm, editable=False)


def update_field_parent(sender, instance, created, **kw):
    """ Updates the timestamp on the parent UIForm when a UIField is saved. """
    print '%s saved: %d' % (sender.__name__, instance.id)
    uiform = instance.uiform
    uiform.last_updated = datetime.now()
    uiform.save()

post_save.connect(update_field_parent, sender=UIField)



class UIFormForm(forms.ModelForm):
    label = forms.CharField(max_length=140, initial='My New UIForm')
    description = forms.CharField(widget=forms.Textarea, 
            initial='A brief description of this form...')

    class Meta:
        model = UIForm
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


            




