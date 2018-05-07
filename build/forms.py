# Stdlib imports

# Core Django imports
from django import forms
from django.contrib.auth.models import User
from .chocolate import replace_all

from lxml import etree
import urllib2, urllib
import datetime

# Third-party app imports

# Imports from apps
from .models import *

# --- USEFUL FUNCTIONS ---
def mission_list():

    starbase_url = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/investigation/Product/'
    list_of_missions = []
    lines = urllib.urlopen(starbase_url).readlines()

    # This prints the start of a table row that contains table data like a link, an img, etc.  
    for lina in lines:
        if 'PDS4_mission' in lina:        
            #print lina

            # We would like to retrieve simply the mission name from the link.  
            # We can easily retrieve this data by turning each line into an etree.
            # Notice, that an etree from a string returns a root and not the whole tree.
            root = etree.fromstring(lina)

            # We then would like to parse the tree to find our wanted data.
            tag_i_want = root[0][0]
            tag_i_want = tag_i_want.attrib.get('href')

            mission_name = tag_i_want[13:]
            mission_name = mission_name[:-8]
            list_of_missions.append(mission_name)

    return list_of_missions

# crawl.mission_tuple takes in a mission_list and turns the list into 2-tuples.
def mission_tuple():
    list_of_missions = mission_list()
    tuple_of_missions = ((k, k.title()) for k in list_of_missions)
    return tuple_of_missions



# crawl.facility_list():
def facility_list():

    starbase_url = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/facility/Product/'
    list_of_facilities_for_url = []
    list_of_facilities_title = []
    lines = urllib.urlopen(starbase_url).readlines()

    # Find lina (spanish word for line) containing PDS4_faciliy.
    for lina in lines:

        if 'PDS4_facility' in lina:  

            # Create a subtree that only contains the contents of the lina.
            # attribute_i_want is the completion of the link to get the new_starbase_url.  
            root = etree.fromstring(lina)
            tag_i_want = root[0][0]
            attribute_i_want = tag_i_want.attrib.get('href')
            list_of_facilities_for_url.append(attribute_i_want)


            # Add the contents of the attribute to the end of the given starbase url and then navigate to said page.
            new_starbase_url = 'https://starbase.jpl.nasa.gov/pds4/context-pds4/facility/Product/{0}'.format(attribute_i_want)
            tree = etree.ElementTree(file=urllib2.urlopen(new_starbase_url))
            root = tree.getroot()
            facility_lid = root[0][0]
            facility_title = root[0][2]
             
            tag_in_question = root[1]
            tag_in_question = etree.QName(tag_in_question)

            if tag_in_question.localname == 'Facility':
                facility_name = root[1][0]
                facility_type_of = root[1][1]

            # This else statement might require future changes.  Currently, this is used for Facility DSN because it has a reference list before the facility tag.  This might require future changes as the facility context products mature.
            else:
                facility_name = root[2][0]
                facility_type_of = root[2][1]
            
            list_of_facilities_title.append(facility_title.text)

            # Get or Create facility object
            facility, created = Facility.objects.get_or_create(title=facility_title.text)
            if created:
                facility.lid = facility_lid.text
                facility.name = facility_name.text
                facility.type_of = facility_type_of.text
                facility.save()
            

    return [list_of_facilities_for_url, list_of_facilities_title]
                

def facility_tuple():

    facilities = facility_list()
    list_of_facilities_for_url = facilities[0]
    list_of_facilities_title = facilities[1]

    tuple_of_facilities = zip(list_of_facilities_for_url, list_of_facilities_title)
    return tuple_of_facilities



# --- END USEFUL FUNCTIONS ---    


# --- FORMS ---
# Create forms here.
class BundleForm(forms.ModelForm):
    name = forms.CharField( initial='Enter name here', required=True, max_length=50) 
    #date_coordinates = forms.DateField(widget=forms.SelectDateWidget(), required=False)     ###
    #time_coordinates = forms.CharField(required=False)


    class Meta:
        model = Bundle              
        fields = ('name', 'version', 'bundle_type',)# 'time_coordinates', 'date_coordinates',)

    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        name = name.lower()
        name = replace_all(name, ' ', '_')
        cleaned_data['name'] = name
        return cleaned_data

class CollectionsForm(forms.ModelForm):
    has_document = forms.BooleanField(required=True, initial=True)
    has_context = forms.BooleanField(required=True, initial=True)
    has_xml_schema = forms.BooleanField(required=True, initial=True)

    class Meta:
        model = Collections
        exclude = ('bundle','name',)

# Data forms
class DataForm(forms.ModelForm):
    PROCESSING_LEVEL_CHOICES = (
        ('calibrated','calibrated'),
        ('derived','derived'),
        ('raw','raw'),
        ('reduced','reduced'),
    )
    DATA_STRUCTURE_CHOICES = (
        ('array','array'),
        ('table','table'),
        ('parsable_byte_stream','parsable byte stream'),
        ('encoded_byte_stream','encoded byte stream'),
    )
    processing_level = forms.ChoiceField(choices=PROCESSING_LEVEL_CHOICES, widget=forms.RadioSelect())
    structure = forms.ChoiceField(choices=DATA_STRUCTURE_CHOICES, widget=forms.RadioSelect())

    class Meta:
        model = Data
        exclude = ('bundle',)

#class TestForm(forms.Form):
   

# Product_Bundle and Submodels
class ProductBundleForm(forms.ModelForm):
    
    class Meta:
        model = Product_Bundle
        exclude = ('bundle','category')

class AliasForm(forms.ModelForm):
    alternate_id = forms.CharField(max_length=200, required=False)
    alternate_title = forms.CharField(max_length=200, required=False)
    comment = forms.CharField(widget=forms.Textarea, required=False) 

    class Meta:
        model = Alias
        exclude = ('bundle',)   


class CitationInformationForm(forms.ModelForm):
    author_list = forms.CharField(required=False)
    description = forms.CharField(widget=forms.TextInput, required=False)
    editor_list = forms.CharField(required=False)
    keyword = forms.CharField(required=False)    
    publication_year = forms.IntegerField(required=False, min_value=1950, max_value=get_three_years_in_future())


    class Meta:
        model = Citation_Information
        exclude = ('bundle', )



def get_years(lowerbound, upperbound):

    year_list = []
    for i in range(upperbound, lowerbound):
        year_list.append((i,i))
        i -= 1
    return year_list


    

# Product_Collection and Submodels
class ProductCollectionForm(forms.ModelForm):
    
    class Meta:
        model = Product_Collection
        exclude = ('bundle','category')


class DocumentForm(forms.ModelForm):
    actual_document = forms.FileField(required=False)

    class Meta:
        model = Document
        fields = ('name', 'title', 'actual_document', 'pds3_label',)


class ConfirmForm(forms.Form):
    CHOICES = [('Yes','Yes') , ('No','No')]
    decision = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())


class DeleteBundleForm(forms.Form):                  # Find this and change to simply ConfirmForm.
    CHOICES = [('Yes','Yes') , ('No','No')]
    decision = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())


# Context Forms
class MissionForm(forms.ModelForm):
    CHOICES = mission_tuple()
    name = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = Mission
        fields = ('name', )

class FacilityForm(forms.ModelForm):
    CHOICES = facility_tuple()
    title = forms.ChoiceField(choices=CHOICES)

    class Meta:
        model = Facility
        fields = ('title',)


class InstrumentHostForm(forms.ModelForm):
    class Meta:
        model = InstrumentHost
        exclude = ('name', 'mission', 'type_of', 'lid', 'raw_data',)


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        exclude = ('name', 'instrument_host', 'type_of', 'lid', 'raw_data',)


class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        exclude = ('name','instrument_host', 'type_of', 'lid', 'raw_data',)



class ChooseInstrumentsForm(forms.Form):

    instrument_list = forms.ModelMultipleChoiceField(queryset=Instrument.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        pk_instrument_host = kwargs.pop('pk_instrument_host', None)
        super(ChooseInstrumentsForm, self).__init__(*args, **kwargs)

        if pk_instrument_host:
            self.fields['instrument_list'].queryset = Instrument.objects.filter(instrument_host=pk_instrument_host)



class ChooseTargetsForm(forms.Form):
    target_list = forms.ModelMultipleChoiceField(queryset=Target.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        pk_instrument_host = kwargs.pop('pk_instrument_host', None)
        super(ChooseTargetsForm, self).__init__(*args, **kwargs)

        if pk_instrument_host:
            self.fields['target_list'].queryset = Target.objects.filter(instrument_host=pk_instrument_host)

    
# Edit Product_Document Forms
class DocumentEditForm(forms.Form):
    revision_id = forms.CharField(max_length=3, initial=1.0)
    author_list = forms.CharField(max_length=100, help_text='Last, F. M.;')
    copyright = forms.CharField(max_length=100)
    publication_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, datetime.datetime.now().year + 3)))
    document_editions = forms.IntegerField(initial='1')
    description = forms.CharField(max_length=400)

class EditDocumentEditionForm(forms.Form):
    edition_name = forms.CharField(max_length=100)
    language = forms.CharField(max_length=100)
    files = forms.IntegerField()

class EditFileForm(forms.Form):
    file_name = forms.CharField(max_length=100)
    local_identifier = forms.CharField(max_length=255)
    document_standard_id = forms.CharField(max_length=100)



# Data Product Templates
class ArrayForm(forms.Form):
    CHOICES = [
        ('Array','Array'),
        ('Array_2D', 'Array 2D'),
        ('Array_2D_Image', 'Array 2D Image'),
        ('Array_2D_Map', 'Array 2D Map'),
        ('Array_2D_Spectrum', 'Array 2D Spectrum'),
        ('Array_3D', 'Array 3D'),
        ('Array_3D_Image', 'Array 3D Image'),
        ('Array_3D_Spectrum', 'Array 3D Spectrum'),
    ]
    array_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())


class TableForm(forms.Form):
    CHOICES = [
        ('Table_Binary','Table Binary'),
        ('Table_Character', 'Table Character'),
        ('Table_Delimited', 'Table Delimited'),
    ]
    table_type = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

class TableCharacterDelimitedForm(forms.Form):
    name = forms.CharField(max_length=100, label='File Name')
    title = forms.CharField(max_length=100)
    fields = forms.IntegerField(min_value=1)
    

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        exclude = ('bundle', 'name', )
    



# --- END FORMS ---    

"""
# -- Context Area and its Submodels
class ContextAreaForm(forms.ModelForm):
    
    class Meta:
        model = Context_Area
        exclude = ('product_bundle','product_collection',)


class ReferenceListForm(forms.ModelForm):
    
    class Meta:
        model = Reference_List
        exclude = ('bundle','product',)


class BundleMemberEntryForm(forms.ModelForm):
  
    class Meta:
        model = Bundle_Member_Entry
        exclude = ('product', 'lid_reference', 'member_status', 'reference_type',)

"""



