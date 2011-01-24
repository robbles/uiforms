from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django import forms

class UIForm(models.Model):
    label = models.CharField(max_length=140)
    description = models.TextField()
    creator = models.ForeignKey(User, editable=False)
    slug = models.SlugField(editable=False)

    def save(self, **kw):
        if not self.id:
            # Populate slug field when first saved
            self.slug = slugify(self.label)
            
        super(UIForm, self).save(**kw)

    @models.permalink
    def get_absolute_url(self):
        return ('update_uiform', [self.creator.username, self.slug])

    def get_fieldform(self):
        """ Create and return a form for creating a new UIField """
        return UIFieldForm()


class UIField(models.Model):
    field_types = (
        ('B', 'Boolean'),
        ('I', 'Integer'),
    )

    label = models.CharField(max_length=50)
    kind = models.CharField(max_length=1, choices=field_types, default='B')
    description = models.TextField()
    uiform = models.ForeignKey(UIForm, editable=False)

    def get_form(self):
        """ Create and return a form for updating this UIField """
        return UIFieldForm(instance=self)


class UIFormForm(forms.ModelForm):
    label = forms.CharField(max_length=140, initial='My New UIForm')
    description = forms.CharField(widget=forms.Textarea, 
            initial='A brief description of this form...')

    class Meta:
        model = UIForm

    def clean_label(self):
        """ Checks to make sure labels are unique per user """
        label = self.cleaned_data['label']
        creator = self.instance.creator
        if UIForm.objects.filter(label=label, creator=creator).count():
            raise forms.ValidationError('You already have a form with this label!')
        return label


class UIFieldForm(forms.ModelForm):
    label = forms.CharField(max_length=140, initial='Field Label')
    description = forms.CharField(widget=forms.Textarea, 
            initial='Description of this field')
    class Meta:
        model = UIField

