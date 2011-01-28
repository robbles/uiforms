from django.contrib import admin
from models import *

class UIFieldInline(admin.StackedInline):
    model = UIField
    extra = 1

class UIFormAdmin(admin.ModelAdmin):
    inlines = [
        UIFieldInline,
    ]

admin.site.register(UIForm, UIFormAdmin)

