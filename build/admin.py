# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.admin import AdminSite

# Register your models here.
from .models import *







# Custom admin classes.------------------------------------------

# Inline Class Declarations
class CollectionsInline(admin.TabularInline):
    model = Collections
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class DocumentInline(admin.TabularInline):
    model = Document
    def has_add_permission(self,request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class InstrumentHostInline(admin.TabularInline):
    model = InstrumentHost
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class InstrumentInline(admin.TabularInline):
    model = Instrument
    def has_add_permissions(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


class TargetInline(admin.TabularInline):
    model = Target
    def has_add_permissions(self, request):
        return False
    def has_delete_permission(self, request):
        return False

class InstrumentInline(admin.TabularInline):
    model = Instrument
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


class TargetInline(admin.TabularInline):
    model = Target
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


# Custom admin classes.----------------------------------
 
 
class BundleAdmin(admin.ModelAdmin):
    inlines = [
        CollectionsInline,
        DocumentInline,
    ]


class MissionAdmin(admin.ModelAdmin):
    inlines = [
        InstrumentHostInline,
    ]


class InstrumentHostAdmin(admin.ModelAdmin):
    inlines = [
        InstrumentInline,
        TargetInline,
    ]







# Register models in admin here.---------------------------------
admin.site.register(InstrumentHost, InstrumentHostAdmin)
admin.site.register(Instrument)
admin.site.register(Target)
admin.site.register(Facility)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Bundle, BundleAdmin)
admin.site.register(Alias)
admin.site.register(Citation_Information)


