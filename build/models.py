# Stdlib imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from .chocolate import *
import datetime

# Final Variables
MAX_CHAR_FIELD = 100
MAX_LID_FIELD = 255
MAX_TEXT_FIELD = 1000

# Helpful functions here.
def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.user.id, filename)

def get_three_years_in_future():
    now = datetime.datetime.now()
    return now.year + 3

# Register your models here.


@python_2_unicode_compatible
class Bundle(models.Model):
    """
    Bundle has a many-one correspondance with User so a User can have multiple Bundles.
    Bundle name is currently not unique and we may want to ask someone whether or not it should be.
    If we require Bundle name to be unique, we could implement a get_or_create so multiple users
    can work on the same Bundle.  However we first must figure out how to click a Bundle and have it
    display the Build-A-Bundle app with form data pre-filled.  Not too sure how to go about this.
    """
    VERSION_CHOICES = (
        ('1.7.0.0', '1.7.0.0'),
        ('1.8.0.0', '1.8.0.0'),
        ('1.9.0.0', '1.9.0.0'),
    )
    BUNDLE_STATUS = (
        ('b', 'Build'),
        ('r', 'Review'),
        ('s', 'Submit'),
    )
    BUNDLE_TYPE_CHOICES = (
        ('Archive', 'Archive'),
        ('Supplemental', 'Supplemental'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    directory = models.CharField(max_length=MAX_TEXT_FIELD, default='Not Created')
    lid = models.CharField(max_length=MAX_LID_FIELD)
    name = models.CharField(max_length=MAX_CHAR_FIELD, unique=True)
    status = models.CharField(max_length=1, choices=BUNDLE_STATUS, blank=False, default='b')     
    bundle_type = models.CharField(max_length=12, choices=BUNDLE_TYPE_CHOICES, default='Archive',)
    version = models.CharField(max_length=7, choices=VERSION_CHOICES, blank=False, default='1.8.0.0') 

    # Returns the url to continue the Build a Bundle process.
    def get_absolute_url(self):
        return reverse('build:bundle_detail', args=[str(self.id)])

    def get_name_title_case(self):          # MINI PROJECT ONE DAY -- Implement for all models
        name_edit = self.name
        name_edit = replace_all(name_edit, '_', ' ')
        return name_edit.title()

    def get_name_directory(self):
        return '{0}_bundle'.format(self.name)

    def __str__(self):
        return self.name  

    class Meta:
        unique_together = ('user', 'name',)


@python_2_unicode_compatible
class Collections(models.Model):
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)
    has_document = models.BooleanField(default=True)
    has_context = models.BooleanField(default=True)
    has_xml_schema = models.BooleanField(default=True)
    has_data = models.BooleanField(default=False)
    has_browse = models.BooleanField(default=False)
    has_calibrated = models.BooleanField(default=False)
    has_geometry = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Collections'

@python_2_unicode_compatible
class Data(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    processing_level = models.CharField(max_length=MAX_CHAR_FIELD)
    structure = models.CharField(max_length=MAX_CHAR_FIELD)
    name = models.CharField(max_length=MAX_CHAR_FIELD)            # FIX FOR CORRECT LID MAYBE
    repetitions = models.IntegerField(default=0);

    def __str__(self):
        return 'data_{}'.format(self.processing_level)

    def get_absolute_url(self):
        return reverse('build:data_template', args=[str(self.bundle.id), str(self.id)])


# Make models for the Array, Table, Parsable_Byte_Stream, and Encoded_Byte_Stream processing levels.





# MAYBE REMOVE
@python_2_unicode_compatible
class Product_Bundle(models.Model):


    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    directory = models.CharField(max_length=MAX_TEXT_FIELD, default='Not Created')
    label = models.CharField(max_length=MAX_TEXT_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)

    
    def __str__(self):
        s = 'Product_Bundle'
        return s


    def get_absolute_url(self):
        """
        Returns the url to continue the Build a Bundle process.
        """
        return reverse('build:product_bundle_detail', args=[str(self.id)])
# --- END REMOVE





    

def get_user_document_directory(instance, filename):
    document_collection_directory = 'archive/{0}/{1}/documents/'.format(instance.bundle.user.username, instance.bundle.name)
    return document_collection_directory

@python_2_unicode_compatible
class Document(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    directory = models.CharField(max_length=MAX_TEXT_FIELD, default='Not Created')
    label = models.CharField(max_length=MAX_TEXT_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD, default='')
    name = models.CharField(max_length=MAX_CHAR_FIELD, unique=True)
    title = models.CharField(max_length=MAX_CHAR_FIELD)
    actual_document = models.FileField(upload_to=get_user_document_directory)
    pds3_label = models.FileField(upload_to=get_user_document_directory)

    def __str__(self):
        return self.name

    def get_edit_url(self):
        """
        Returns the url to further edit the document label.
        """
        return reverse('build:document_edit', args=[str(self.bundle.id), str(self.id)])

    def get_archive_url(self):
        """
        Returns the url to the product document's xml label located in the archive.
        """
        return reverse('main:construction')



# MAYBE REMOVE
@python_2_unicode_compatible
class Product_Collection(models.Model):


    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    directory = models.CharField(max_length=MAX_TEXT_FIELD, default='Not Created')
    label = models.CharField(max_length=MAX_TEXT_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)
    category = models.CharField(max_length=20) # MAYBE ADD CHOICES FOR COLLECTION TYPES

    
    def __str__(self):
        s = 'Product_Collection'
        return s


    def get_absolute_url(self):
        """
        Returns the url to continue the Build a Bundle process.
        """
        return reverse('build:product_collection_detail', args=[str(self.id)])
# --- END REMOVE ---

@python_2_unicode_compatible
class Mission(models.Model):
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    bundle = models.ManyToManyField(Bundle)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        
        # Returns the url to continue the Crawl Starbase process.        
        return reverse('crawl_starbase:mission_detail', args=[str(self.id)])

@python_2_unicode_compatible
class Facility(models.Model):
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)
    title = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=20)
    bundle = models.ManyToManyField(Bundle)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class InstrumentHost(models.Model):
    CHOICES = ( ('Laboratory', 'Laboratory'), ('Observatory', 'Observatory'), )
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_CHAR_FIELD, choices=CHOICES)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)
    raw_data = models.CharField(max_length=MAX_CHAR_FIELD)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        
        return reverse('crawl_starbase:instrument_host_detail', args=[str(self.id)])


   # def get_absolute_url(self):
   #     
   #     # Returns the url to continue the Crawl Starbase process.
   #     return reverse('crawl_starbase:instrumenthost_detail', args=[str(self.id)])


# After talking to Lynn, change Instrument and Target to submodel Instrument_Host rather than Mission.
# Then change views and stuff to follow accordingly.  Also change admin so that Spacecraft is the 
# main and Instrument and Target are inlines.
@python_2_unicode_compatible
class Instrument(models.Model):
    instrument_host = models.ForeignKey(InstrumentHost, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)
    raw_data = models.CharField(max_length=MAX_CHAR_FIELD)
    bundle = models.ManyToManyField(Bundle, blank=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Target(models.Model):
    instrument_host = models.ForeignKey(InstrumentHost, on_delete=models.CASCADE)
    title = models.CharField(max_length=MAX_CHAR_FIELD)
    type_of = models.CharField(max_length=MAX_CHAR_FIELD)
    lid = models.CharField(max_length=MAX_LID_FIELD)
    raw_data = models.CharField(max_length=MAX_CHAR_FIELD)
    bundle = models.ManyToManyField(Bundle, blank=True)

    def __str__(self):
        return self.title

class Choice_Instruments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instrument = models.ManyToManyField(Instrument)


# Information_Area Models
@python_2_unicode_compatible
class Citation_Information(models.Model):
    bundle = models.OneToOneField(Bundle, on_delete=models.CASCADE)    
    author_list = models.CharField(max_length=MAX_CHAR_FIELD, help_text="Lastname, F. M.; ")
    description = models.CharField(max_length=MAX_TEXT_FIELD)
    editor_list = models.CharField(max_length=MAX_CHAR_FIELD, help_text="Lastname, F. M.; ")
    keyword = models.CharField(max_length=MAX_CHAR_FIELD)
    publication_year = models.DateField()                    #############

    def __str__(self):
        return 'Author List: {0}, Publication Year: {1},'.format(self.author_list, self.publication_year)

# Boolean Models
@python_2_unicode_compatible
class Alias(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    alternate_id = models.CharField(max_length=MAX_CHAR_FIELD)
    alternate_title = models.CharField(max_length=MAX_CHAR_FIELD)
    comment = models.CharField(max_length=MAX_TEXT_FIELD)

    def __str__(self):
        if self.alternate_id:
            return self.alternate_id
        elif self.alternate_title:
            return self.title
        elif self.comment:
            return self.comment
        else:
            return 'Alias does not have an id, title, or comment.  Alias is invalid.'

    def get_delete_url(self):
        return reverse('build:alias_delete', args=[str(self.bundle.pk), str(self.pk)])

    class Meta:
        verbose_name_plural = 'Aliases'


# --- DELETE ---
@python_2_unicode_compatible
class Template(models.Model):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_CHAR_FIELD)
    

    def __str__(self):
        return self.name

# --- END DELETE ---









