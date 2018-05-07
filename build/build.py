# build.py
# Author: @PieceOfKayk
#
# 
# This script contains function definitions for building bundles.
# Notice there are imports for the label app.  This is because the label app specifically contains
# models used within labels.  The label app is seperate from build_a_bundle because there will be 
# another app like build_a_bundle but it will be search_a_bundle in which we can add preexisting
# mission data to fill in parts of the build_a_bundle app for us. But that comes way later.
import os
from lxml import etree
from xml.dom import minidom
from copy import deepcopy
from django.conf import settings
from .forms import *
from .chocolate import *
from main.models import Joke

import datetime
import random
#from . import create, grow, write


#    -    -    -    -    -    -    -    -    -    -    -    -    -    -    -    -    -    -
# FINAL VARIABLES


# The namespace map is the final variable used to add a namespace to the PDS4 labels.  XML uses a namespace to... [fill in the blank].
NAMESPACE_MAP = {
                    None: 'http://pds.nasa.gov/pds4/pds/v1',
                    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                      
    }

# Need info about namespace map for product observational right here
NAMESPACE_MAP_PRODUCT_OBSERVATIONAL = {
    None: 'http://pds.nasa.gov/pds4/pds/v1',
    'pds': 'http://pds.nasa.gov/pds4/pds/v1',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    #'schemaLocation': 'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/schema/released/pds/v1/PDS4_PDS_1700.xsd',

    }




####################### NOTE:  The request attribute is in all of the below functions however it is used in only the Bundle function.  Do a ctrl+f 'request' to see what I mean.  The request attribute can be taken out of all functions that do not use a request within the function.  If request is removed as an attribute, it must be removed as a function wherever the function is called.  For example, the build.Collections function has an unused request attribute.  In views.py it is called in views.index with the line build.Collections(request, form_collections, bundle).  Change the function call to build.Collections(form_collections, bundle) and change the function definition to def Collections(form, bundle).

# - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  
# Bundle Functions. 


# build.Bundle takes in a request and a user-filled form to:
#     1. Create a Django Bundle model object
#     2. Create a bundle directory in the user directory, which is located in the public archive.
#     3. Create the Product_Bundle label to be placed in the bundle directory where Product_Bundle is specific to the Bundle model object. 
def Bundle(request, form):

    # Create Bundle Model.
    bundle = form.save(commit=False)
    bundle.user = request.user
    #bundle.bundle_type = 'Primary'
    bundle.lid = 'urn:{0}:{1}'.format(request.user.userprofile.agency, bundle.name)
    bundle.status = 'b' # b for build.  New Bundles are always in build stage first.

    # Create Bundle Directory and add to Bundle Model.
    bundle_directory_name = '{}_bundle'.format(bundle.name)
    user_name = bundle.user.username
    user_path = os.path.join(settings.ARCHIVE_DIR, user_name)
    bundle_path = os.path.join(user_path, bundle_directory_name)
    make_directory(bundle_path)
    bundle.directory = bundle_path
    bundle.save()

    # Make Product_Bundle
    #     1. Grow Product_Bundle tree.
    Product_Bundle_Root = etree.Element('Product_Bundle', nsmap = NAMESPACE_MAP)
    Identification_Area = etree.SubElement(Product_Bundle_Root, 'Identification_Area')    
    Context_Area = etree.SubElement(Product_Bundle_Root, 'Context_Area')
    Reference_List = etree.SubElement(Product_Bundle_Root, 'Reference_List')
    Bundle = etree.SubElement(Product_Bundle_Root, 'Bundle')

    #     2. Grow Identification_Area
    logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
    logical_identifier.text = bundle.lid
    version_id = etree.SubElement(Identification_Area, 'version_id')
    version_id.text = '1.0'
    title = etree.SubElement(Identification_Area, 'title')
    bundle_title = title_case(bundle.name)   # MINI PROJECT - Change to a model function
    title.text = bundle_title
    information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
    information_model_version.text = bundle.version
    product_class = etree.SubElement(Identification_Area, 'product_class')
    product_class.text = 'Product_Bundle'        
    Alias_List = etree.SubElement(Identification_Area, 'Alias_List')
    Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')
    Modification_History = etree.SubElement(Identification_Area, 'Modification_History')    

    #     3. Grow Context_Area
    Time_Coordinates = etree.SubElement(Context_Area, 'Time_Coordinates')
    Investigation_Area = etree.SubElement(Context_Area, 'Investigation_Area')
    Observing_System = etree.SubElement(Context_Area, 'Observing_System')
    name = etree.SubElement(Observing_System, 'name')
    

    #     4. Write Product_Bundle to file in User Bundle Directory
    label = 'bundle_{0}.xml'.format(bundle.name)
    label_path = os.path.join(bundle_path, label)
    label = open(label_path, 'w+')
    tree = etree.tostring(Product_Bundle_Root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(tree)
    label.close()

    # Create Product type Bundle.
    product = ProductBundleForm().save(commit=False)
    product.bundle = bundle
    #product.category = 'Bundle'
    product.directory = bundle.directory
    product.label = label_path
    product.lid = bundle.lid
    product.save()
  
    return bundle


# - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  
# Collection Functions.


# build.Collections takes in a request, a user-filled form and a Bundle model object.
#     In PDS4, a Bundle has collections.  For each collection in a bundle, a collection directory is placed (within the bundle directory) and a Product_Collection label is created.  
def Collections(request, form, bundle):

    # Create Collections Model Object and list of Collections, list of Collectables
    collections = form.save(commit=False)
    collections.bundle = bundle
    collections.save()

    # Collections List
    collections_list = ['document', 'context', 'xml_schema']

    # if collections.has_data:
        #collections_list.append('data') --> Removed from list so that a label is not created.

        # Create directory
        # collection_dir = os.path.join(bundle.directory, 'data')  --- 2018 Don't mk data a directory
        # make_directory(collection_dir)

        # Create data model				# MOVED: the creation of the Data model object
        # form_data = DataForm().save(commit=False)     # is now implemented into the Data collection 
        # form_data.bundle = bundle                     # page.  MAR 2018
        # form_data.save()

    if collections.has_browse:
        collections_list.append('browse')

    if collections.has_calibrated:
        collections_list.append('calibrated')

    if collections.has_geometry:
        collections_list.append('geometry')    

    

    # Iterate through collection list, creating Product and its base Product Submodels.
    for collection in collections_list:

        # Create Collection Directory
        collection_dir = os.path.join(bundle.directory, collection)
        make_directory(collection_dir)


        # Make Product_Collection
        #     1. Grow Product_Collection tree.
        Product_Collection = etree.Element('Product_Collection', nsmap = NAMESPACE_MAP)
        Identification_Area = etree.SubElement(Product_Collection, 'Identification_Area')
        Context_Area = etree.SubElement(Product_Collection, 'Context_Area')
        Collection = etree.SubElement(Product_Collection, 'Collection')
        File_Area_Inventory = etree.SubElement(Product_Collection, 'File_Area_Inventory')

        
        #     2. Fill Identification_Area
        logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
        collection_lid = '{0}:{1}'.format(bundle.lid, collection)
        logical_identifier.text = collection_lid
        version_id = etree.SubElement(Identification_Area, 'version_id')
        version_id.text = '1.0'
        title = etree.SubElement(Identification_Area, 'title')
        title.text = '{0} {1} Collection'.format(title_case(bundle.name), title_case(collection))  # MINI PROJECT - Change to a model function
        information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
        information_model_version.text = bundle.version
        product_class = etree.SubElement(Identification_Area, 'product_class')
        product_class.text = 'Product_Collection'
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')
        Modification_History = etree.SubElement(Identification_Area, 'Modification_History')

        #     3. Grow Context_Area
        Time_Coordinates = etree.SubElement(Context_Area, 'Time_Coordinates')
        Investigation_Area = etree.SubElement(Context_Area, 'Investigation_Area')
        Observing_System = etree.SubElement(Context_Area, 'Observing_System')
        name = etree.SubElement(Observing_System, 'name')

        #     4. Fill Collection
        collection_type = etree.SubElement(Collection, 'collection_type')
        collection_name = collection
        collection_name = replace_all(collection_name, '_', ' ')
        collection_type.text = collection_name.title()

        #     5. Write Product_Collection label.  
        label = 'collection_{0}_{1}.xml'.format(bundle.name, collection)
        label_path = os.path.join(collection_dir, label)
        label = open(label_path, 'w+')
        tree = etree.tostring(Product_Collection, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(tree)
        label.close()

        # Create Product model object.
        product = ProductCollectionForm().save(commit=False)
        product.bundle = bundle
        product.directory = collection_dir
        product.label = label_path
        product.category = collection
        product.lid = collection_lid
        product.save()

        # Add Bundle Member Entry for collection in Product Bundle label
        #    1. Get Product 
        product_bundle = Product_Bundle.objects.get(bundle=bundle)
        label = product_bundle.label
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(label, parser)
        label_file = open(label, 'w+')

        #    2. Locate and write BME to Tree.
        root = tree.getroot()
        Bundle_Member_Entry = etree.SubElement(root, 'Bundle_Member_Entry')
        lid_reference = etree.SubElement(Bundle_Member_Entry, 'lid_reference')
        lid_reference.text = collection_lid
        member_status = etree.SubElement(Bundle_Member_Entry, 'member_status')
        member_status.text = 'Primary'
        reference_type = etree.SubElement(Bundle_Member_Entry, 'reference_type')
        reference_type.text = 'bundle_has_{}_collection'.format(collection)
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label_file.write(bundle_tree)
        label_file.close()
       
    return  


# build.Document takes in a request, a user-filled form, and a Bundle model object.
#    One of three required collections in a bundle is the document collection.
#    The document collection contains documents.
#    For each document the user adds:
#        A. a Document model object is created
#        B. a Product_Document label is created.
#        C. the File_Area_Inventory of the Document's Product_Collection label is updated
#        D. the Reference_List of the Product_Bundle label is updated
def Document(request, form, bundle):
    print 'DEBUG build.Document'
    print '-- bundle id: {0}'.format(bundle.id)
    print '-- bundle name: {0}'.format(bundle.name)
    print '-- bundle lid: {0}'.format(bundle.lid)


    # Find Documents directory
    bundle_dir = bundle.directory
    document_dir = os.path.join(bundle_dir, 'document')
    print document_dir


    # Get name of document label.
    name = str(form['name'].value())
    title = str(form['title'].value())

    # Clean name for Title case
    title_name = title_case(title)

    # Clean name for lid
    lid_name = lid_case(name)
    lid = '{0}:{1}:{2}'.format(bundle.lid, 'document', lid_name)

    # Create the label_path and open the (new) file located at the label_path
    label = '{0}.xml'.format(lid_name)
    label_path = os.path.join(document_dir, label)
    label = open(label_path, 'w+')

    # A. Make Document model object                ---- Currently Broken ---- ?? IDK IF TRUE 8/15/17
    document = form.save(commit=False)
    document.bundle = bundle
    document.lid = lid
    document.directory = document_dir
    document.label = label_path
    document.save() 

    # B. Make Product_Document
    #     1. Grow Product Document Tree
    Product_Document = etree.Element('Product_Document', nsmap=NAMESPACE_MAP)
    Identification_Area = etree.SubElement(Product_Document, 'Identification_Area')
    Reference_List = etree.SubElement(Product_Document, 'Reference_List')
    Document = etree.SubElement(Product_Document, 'Document')

    #     2. Fill tree with current information - Identification Area
    logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
    logical_identifier.text = lid
    version_id = etree.SubElement(Identification_Area, 'version_id')
    version_id.text = '1.0'
    title = etree.SubElement(Identification_Area, 'title')
    title.text = title_name
    information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
    information_model_version.text = bundle.version
    product_class = etree.SubElement(Identification_Area, 'product_class')
    product_class.text = 'Product_Document'

    number_of_cites = Citation_Information.objects.filter(bundle=bundle).count()
    Citation_Information_Tag = etree.SubElement(Identification_Area, 'Citation_Information')

    if number_of_cites == 1:
        # then Citation_Information has been added to the bundle so we must fill in this part of the label
        cite = Citation_Information.objects.get(bundle=bundle)
        if cite.author_list:
            author_list = etree.SubElement(Citation_Information_Tag, 'author_list')
            author_list.text = cite.author_list
        if cite.publication_year:
            publication_year = etree.SubElement(Citation_Information_Tag, 'publication_year')
            publication_year.text = cite.publication_year
        if cite.keyword:
            keyword = etree.SubElement(Citation_Information_Tag, 'keyword')
            keyword.text = cite.keyword
        if cite.description:
            description = etree.SubElement(Citation_Information_Tag, 'description')
            description.text = cite.description
                    
    Modification_History = etree.SubElement(Identification_Area, 'Modification_History')


    #     3. Fill tree with current information - Reference List
    #Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')
    #lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
    #lid_reference.text = '{}:context:instrument:_____'.format(bundle.lid)
    #reference_type = etree.SubElement(Internal_Reference, 'reference_type')
    #reference_type.text = 'document_to_instrument'
    #External_Reference = etree.SubElement(Reference_List, 'External_Reference')
    #reference_text = etree.SubElement(External_Reference, 'reference_text')
    #description = etree.SubElement(External_Reference, 'description')

    #     4. Fill tree with current information - Document
    #revision_id = etree.SubElement(Document, 'revision_id')
    #revision_id.text = '1.0'
    #document_name = etree.SubElement(Document, 'document_name')
    #author_list = etree.SubElement(Document, 'author_list')
    #copyright = etree.SubElement(Document, 'copyright')
    #publication_date = etree.SubElement(Document, 'publication_date')
    #publication_date.text = 'yyyy-mm-dd'
    #document_editions = etree.SubElement(Document, 'document_editions')
    #document_editions.text = '1'
    #description = etree.SubElement(Document, 'description')
    #Document_Edition = etree.SubElement(Document, 'Document_Edition')
    #edition_name = etree.SubElement(Document_Edition, 'edition_name')
    #language = etree.SubElement(Document_Edition, 'language')
    #files = etree.SubElement(Document_Edition, 'files')
    #files.text = '1'
    #Document_File = etree.SubElement(Document_Edition, 'Document_File')
    #file_name = etree.SubElement(Document_File, 'file_name')
    #local_identifier = etree.SubElement(Document_File, 'local_identifier')
    #document_standard_id = etree.SubElement(Document_File, 'document_standard_id')


    #     5. Write Product_Document label.  
    tree = etree.tostring(Product_Document, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(tree)
    label.close()
 

    # C. Add Document info to the Document Collection Product under File_Area_Inventory
    #     1.  Find Product_Collection label for the Document collection
    label = 'collection_{}_document.xml'.format(bundle)
    label_path = os.path.join(document_dir, label)
    print label_path
    
    #     2. Create Parser
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label_path, parser)
    label = open(label_path, 'w')

    #     3. Do what needs to be done
    Product_Collection = tree.getroot()
    File_Area_Inventory = Product_Collection[3]
    File = etree.SubElement(File_Area_Inventory, 'File')
    file_name = etree.SubElement(File, 'file_name')
    file_name.text = document.title
    local_identifier = etree.SubElement(File, 'local_identifier')
    local_identifier.text = document.name
    creation_date_time = etree.SubElement(File, 'creation_date_time')
    creation_date_time.text = str(datetime.datetime.now())

    #     4. Write Product_Collection for the document collection
    tree = etree.tostring(Product_Collection, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(tree)
    label.close()
    

    # D. Add Document info to the Product Bundle under Reference_List
    #     1. Find Product_Bundle label
    label = 'bundle_{}.xml'.format(bundle)
    label_path = os.path.join(bundle_dir, label)
    print label_path

    #     2. Create Parser
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label_path, parser)
    label = open(label_path, 'w')

    #     3. Do what needs to be done
    Product_Bundle = tree.getroot()
    Reference_List = Product_Bundle[2]
    Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')
    lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
    lid_reference.text = document.lid
    reference_type = etree.SubElement(Internal_Reference, 'reference_type')
    reference_type.text = 'bundle_to_document'

    #     4. Write Product_Bundle
    tree = etree.tostring(Product_Collection, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(tree)
    label.close()

    
# - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  
# Product_Bundle Editors

# build.Alias takes in a user-filled form and a Product_Bundle model object
def Alias(form, product_bundle):


    # Make Alias Model Object
    alias = form.save(commit=False)
    alias.bundle = product_bundle.bundle
    alias.save()

    # Find Product_Bundle Label
    label = product_bundle.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')

    # Locate Alias List in tree and edit
    root = tree.getroot()
    Alias_List = root[0][5]
    Alias = etree.SubElement(Alias_List, 'Alias')

    if form.cleaned_data['alternate_id']:
        alternate_id = etree.SubElement(Alias, 'alternate_id')
        alternate_id.text = alias.alternate_id

    if form.cleaned_data['alternate_title']:
        alternate_title = etree.SubElement(Alias, 'alternate_title')
        alternate_title.text = alias.alternate_title

    if form.cleaned_data['comment']:
        comment_tag = etree.SubElement(Alias, 'comment')
        comment_tag.text = alias.comment

    bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label_file.write(bundle_tree)
    label_file.close()



def AliasRemove(alias, product_bundle):   

    # Find Product_Bundle Label
    label = product_bundle.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')


    # Find Alias
    root = tree.getroot()
    Alias_List = root[0][5]
        # Still need to learn how to traverse through an xml tree.

    


def CitationInformation(form, bundle):

    # Make Citation_Information model object                                 
    citation_information = form.save(commit=False)
    citation_information.bundle = bundle
    publication_date = form.cleaned_data['publication_year']
    publication_yr = str(publication_date)[:4]
    citation_information.publication_year = publication_yr
    citation_information.save()


    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:
        print xml_path

        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        if is_product_bundle(xml_path):
            Citation_Information = root[0][6]
        else:
            Citation_Information = root[0][5]


        # Required fields: publication_year and description
        publication_year = etree.SubElement(Citation_Information, 'publication_year')
        publication_year.text = citation_information.publication_year
        description = etree.SubElement(Citation_Information, 'description')
        description.text = citation_information.description

        # Fields not required: author_list, editor_list, keyword
        if form.cleaned_data['author_list']:
            author_list = etree.SubElement(Citation_Information, 'author_list')
            author_list.text = citation_information.author_list
        if form.cleaned_data['editor_list']:
            editor_list = etree.SubElement(Citation_Information, 'editor_list')
            editor_list.text = citation_information.editor_list
        if form.cleaned_data['keyword']:
            keyword = etree.SubElement(Citation_Information, 'keyword')
            keyword.text = citation_information.keyword


        # Sum up the tree
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(bundle_tree)
        label.close()


# ------------------------------------------------------------------------------------
def DataSet(form, bundle):

    # Make Data model object
    data = form.save(commit=False)
    data.bundle = bundle
    data.save()

    # Now that we have a Data model object with a given data type, we must see if that type already exists in the bundle.  We do this by checking if the data_type collection is present in the directory.  If the data_type collection exists, do nothing.  If it doesn't exist, we simply need to create the collection directory.

    # Create Data Type Directory
    data_name = 'data_{}'.format(data.processing_level)
    data_dir = os.path.join(bundle.directory, data_name)
    make_directory(data_dir)
    
# ------- NOTE
#         We need to edit the following section to add citation_info, alias, etc if it's already been added to the bundle.
    # If Product_Collection does not exist, create Product_Collection
    product_collection = 'archive/{0}/{1}_bundle/data_{2}/collection_{3}_{4}'.format(bundle.user, bundle.name, data.processing_level, bundle.name, data)
    if not (os.path.exists(product_collection)):
        # Make Product_Collection
        #     1. Grow Product_Collection tree.
        Product_Collection = etree.Element('Product_Collection', nsmap = NAMESPACE_MAP)
        Identification_Area = etree.SubElement(Product_Collection, 'Identification_Area')
        Context_Area = etree.SubElement(Product_Collection, 'Context_Area')
        Collection = etree.SubElement(Product_Collection, 'Collection')
        File_Area_Inventory = etree.SubElement(Product_Collection, 'File_Area_Inventory')

        
        #     2. Fill Identification_Area
        logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
        collection_lid = '{0}:{1}'.format(bundle.lid, data)
        logical_identifier.text = collection_lid
        version_id = etree.SubElement(Identification_Area, 'version_id')
        version_id.text = '1.0'
        title = etree.SubElement(Identification_Area, 'title')
        title.text = '{0} Data {1} Collection'.format(title_case(bundle.name), title_case(data.processing_level))  # MINI PROJECT - Change to a model function
        information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
        information_model_version.text = bundle.version
        product_class = etree.SubElement(Identification_Area, 'product_class')
        product_class.text = 'Product_Collection'
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')
        Modification_History = etree.SubElement(Identification_Area, 'Modification_History')

        #     3. Grow Context_Area
        Time_Coordinates = etree.SubElement(Context_Area, 'Time_Coordinates')
        Investigation_Area = etree.SubElement(Context_Area, 'Investigation_Area')
        Observing_System = etree.SubElement(Context_Area, 'Observing_System')
        name = etree.SubElement(Observing_System, 'name')

        #     4. Fill Collection
        collection_type = etree.SubElement(Collection, 'collection_type')
        collection_type.text = 'Data {}'.format(data.processing_level.title())

        #     5. Write Product_Collection label.  
        label = 'collection_{0}_{1}.xml'.format(bundle.name, data)
        label_path = os.path.join(data_dir, label)
        label = open(label_path, 'w+')
        tree = etree.tostring(Product_Collection, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(tree)
        label.close()

    return data


def DataTemplate(form, data):

    bundle = data.bundle
    
    # Find Data Collection directory
    data_name = 'data_{}'.format(data.processing_level)
    data_dir = os.path.join(bundle.directory, data_name)

    # Make Product_Observational
    #     1. Grow Product_Observational tree.
    Product_Observational = etree.Element('Product_Observational', nsmap = NAMESPACE_MAP)
    Identification_Area = etree.SubElement(Product_Observational, 'Identification_Area')
    Observation_Area = etree.SubElement(Product_Observational, 'Observation_Area')
    Reference_List = etree.SubElement(Product_Observational, 'Reference_List')
    File_Area_Observational = etree.SubElement(Product_Observational, 'File_Area_Observational')

    #     2. Grow Identification Area
    logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
    logical_Identifier.text = 'urn:nasa:pds:{}:{}:{}'.format(bundle, data, data.name)
    version_id = etree.SubElement(Identification_Area, 'version_id')
    version_id = '1.0'
    title = etree.SubElement(Identification_Area, 'title')
    title.text = data.name
    information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
    information_model_version.text = bundle.version

    #     3. Grow Observation Area
    Time_Coordinates = etree.SubElement(Observation_Area, 'Time_Coordinates')
    start_date_time = etree.SubElement(Time_Coordinates, 'start_date_time')
    stop_date_time = etree.SubElement(Time_Coordinates, 'stop_date_time')
    Primary_Result_Summary = etree.SubElement(Observation_Area, 'Primary_Result_Summary')
    purpose = etree.SubElement(Primary_Result_Summary, 'purpose')
    purpose.text = 'Science'
    processing_level = etree.SubElement(Primary_Result_Summary, 'processing_level')
    processing_level.text = data.processing_level
    Science_Facets = etree.SubElement(Primary_Result_Summary, 'Science_Facets')
    domain = etree.SubElement(Science_Facets, 'domain')
    domain.text = 'Atmosphere'
    discipline_name = etree.SubElement(Science_Facets, 'discipline_name')
    discipline_name.text = 'Atmospheres'
    facet1 = etree.SubElement(Science_Facets, 'facet1')
    Investigation_Area = etree.SubElement(Observation_Area, 'Investigation_Area')
    name = etree.SubElement(Investigation_Area, 'name')
    investigation_type = etree.SubElement(Investigation_Area, 'type')
    Internal_Reference = etree.SubElement(Investigation_Area, 'Internal_Reference')
    lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
    lid_reference = 'urn:nasa:pds:context:investigation:{}'.format(data.name)
    reference_type = etree.SubElement(Internal_Reference, 'reference_type')
    reference_type.text = 'data_to_investigation'

    #     Grow File_Area_Observational
    File = etree.SubElement(File_Area_Observational, 'File')
    file_name = etree.SubElement(File, 'file_name')
    local_identifier = etree.SubElement(File, 'local_identifier')
    creation_date_time = etree.SubElement(File, 'creation_date_time')
    file_size = etree.SubElement(File, 'file_size')                   ############ HERE
    records = etree.SubElement(File, 'records')

    #     The next section of the label is dependent upon the data structure.
    if data.structure == 'table_character':
        Table_Character = etree.SubElement(File_Area_Observational, 'Table_Character')
        name = etree.SubElement(Table_Character, 'name')
        local_identifier = etree.SubElement(Table_Character, 'local_identifier')
        offset = etree.SubElement(Table_Character, 'offset')         ########## HERE
        object_length = etree.SubElement(Table_Character, 'object_length')
        parsing_standard_id = etree.SubElement(Table_Character, 'parsing_standard_id')
        parsing_standard_id.text = 'PDS DSV 1'
        description = etree.SubElement(Table_Character, 'description')
        records = etree.SubElement(Table_Character, 'records')
        record_delimiter = etree.SubElement(Table_Character, 'record_delimiter')
        record_delimiter.text = 'Carriage-Return Line-Feed'
        Record_Character = etree.SubElement(Table_Character, 'Record_Character')
        fields = etree.SubElement(Record_Character, 'fields')
        groups = etree.SubElement(Record_Character, 'groups')

        # the following part of the Record_Character is repeated given the # of fields above
        Field_Character = etree.SubElement(Record_Character, 'Field_Character')
        name = etree.SubElement(Field_Character, 'name')
        field_location = etree.SubElement(Field_Character, 'field_location')
        data_type = etree.SubElement(Field_Character, 'data_type')
        field_length = etree.SubElement(Field_Character, 'field_length')
        field_number = etree.SubElement(Field_Character, 'field_number')
        description = etree.SubElement(Field_Character, 'description')







def TableDelimited(form, bundle, data_type):
    the_name = form.cleaned_data['name']
    the_title = form.cleaned_data['title']
    number_of_fields = form.cleaned_data['fields']

    # Get or Create folder of specified data_type (like raw, calibrated, etc)
    data_path = os.path.join(bundle.directory, 'data')
    data_variable = 'data_{}'.format(data_type)  # Makes bundle/data/data_raw versus bundle/data/raw
    data_type_path = os.path.join(data_path, data_variable)
    created_directory = make_directory(data_type_path)

    if created_directory:
        # Make Product_Collection
        #     1. Grow Product_Collection tree.
        Product_Collection = etree.Element('Product_Collection', nsmap = NAMESPACE_MAP)
        Identification_Area = etree.SubElement(Product_Collection, 'Identification_Area')
        Context_Area = etree.SubElement(Product_Collection, 'Context_Area')
        Collection = etree.SubElement(Product_Collection, 'Collection')
        File_Area_Inventory = etree.SubElement(Product_Collection, 'File_Area_Inventory')

        
        #     2. Fill Identification_Area
        logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
        collection_lid = '{0}:data_{1}'.format(bundle.lid, data_type)
        logical_identifier.text = collection_lid
        version_id = etree.SubElement(Identification_Area, 'version_id')
        version_id.text = '1.0'
        title = etree.SubElement(Identification_Area, 'title')
        title.text = ''
        information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
        information_model_version = bundle.version
        product_class = etree.SubElement(Identification_Area, 'product_class')
        product_class.text = 'Product_Collection'
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')
        Modification_History = etree.SubElement(Identification_Area, 'Modification_History')

        #     3. Grow Context_Area
        Time_Coordinates = etree.SubElement(Context_Area, 'Time_Coordinates')
        Investigation_Area = etree.SubElement(Context_Area, 'Investigation_Area')
        Observing_System = etree.SubElement(Context_Area, 'Observing_System')
        name = etree.SubElement(Observing_System, 'name')

        #     4. Fill Collection
        collection_type = etree.SubElement(Collection, 'collection_type')
        collection_name = 'data_{}'.format(data_type)
        collection_name = replace_all(collection_name, '_', ' ')
        collection_type.text = collection_name.title()

        #     5. Write Product_Collection label.  
        label = 'collection_{0}_{1}.xml'.format(bundle.name, data_type)
        label_path = os.path.join(path, label)
        label = open(label_path, 'w+')
        tree = etree.tostring(Product_Collection, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(tree)
        label.close()

        # Create Product model object.
        product = ProductCollectionForm().save(commit=False)
        product.bundle = bundle
        product.directory = path
        product.label = label_path
        product.category = 'data_{}'.format(data_type)
        product.lid = collection_lid
        product.save()

        # Add Bundle Member Entry for collection in Product Bundle label
        #    1. Get Product 
        product_bundle = Product_Bundle.objects.get(bundle=bundle)
        label = product_bundle.label
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(label, parser)
        label_file = open(label, 'w+')

        #    2. Locate and write BME to Tree.
        root = tree.getroot()
        Bundle_Member_Entry = etree.SubElement(root, 'Bundle_Member_Entry')
        lid_reference = etree.SubElement(Bundle_Member_Entry, 'lid_reference')
        lid_reference.text = collection_lid
        member_status = etree.SubElement(Bundle_Member_Entry, 'member_status')
        member_status.text = 'Primary'
        reference_type = etree.SubElement(Bundle_Member_Entry, 'reference_type')
        reference_type.text = 'bundle_has_data_{}_collection'.format(data_type)
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label_file.write(bundle_tree)
        label_file.close()
    
    # Add table character delimited template label to data directory
    #    1. Declare root and namespace
    Product_Observational = etree.Element('Product_Observational', nsmap = NAMESPACE_MAP_PRODUCT_OBSERVATIONAL)

    #    2. Build children of Root
    Identification_Area = etree.SubElement(Product_Observational, 'Identification_Area')
    Observation_Area = etree.SubElement(Product_Observational, 'Observation_Area')
    Reference_List = etree.SubElement(Product_Observational, 'Reference_List')
    File_Area_Observational = etree.SubElement(Product_Observational, 'File_Area_Observational')
    File_Area_Observational_Supplemental = etree.SubElement(Product_Observational, 'File_Area_Observational_Supplemental')

    #    3. Build Identification_Area
    logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
    lid = '{0}:{1}:{2}'.format(bundle.lid, data_type, the_name)
    logical_identifier.text = lid
    version_id = etree.SubElement(Identification_Area, 'version_id')
    version_id.text = '1.0'
    title = etree.SubElement(Identification_Area, 'title')
    title.text = the_title
    information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
    information_model_version.text = bundle.version

    #    4. Build Observation Area
    Time_Coordinates = etree.SubElement(Observation_Area, 'Time_Coordinates')
    start_date_time = etree.SubElement(Time_Coordinates, 'start_date_time')
    start_date_time.text = '____'
    stop_date_time = etree.SubElement(Time_Coordinates, 'stop_date_time')
    stop_date_time.text = '____'
    Primary_Result_Summary = etree.SubElement(Observation_Area, 'Primary_Result_Summary')
    purpose = etree.SubElement(Primary_Result_Summary, 'purpose')
    purpose.text = 'Science'
    processing_level = etree.SubElement(Primary_Result_Summary, 'processing_level')
    processing_level.text = 'Derived'
    Science_Facets = etree.SubElement(Primary_Result_Summary, 'Science_Facets')
    domain = etree.SubElement(Science_Facets, 'domain')
    domain.text = 'Atmospheres'
    discipline_name = etree.SubElement(Science_Facets, 'discipline_name')
    discipline_name.text = 'Atmospheres'
    facet1 = etree.SubElement(Science_Facets, 'facet1')
    facet1.text = '____'

    #    5. Build File Area Observational Area
    File = etree.SubElement(File_Area_Observational, 'File')
    file_name = etree.SubElement(File, 'file_name')
    file_name.text = '____'
    local_identifier = etree.SubElement(File, 'local_identifier')
    local_identifier.text = '____'
    creation_date_time = etree.SubElement(File, 'creation_date_time')
    creation_date_time.text = 'YYYY-MM-DDThh:mm:ss'
    file_size = etree.SubElement(File, 'file_size', unit='byte')
    file_size.text = '____'
    records = etree.SubElement(File, 'records')
    records.text = '____'
    Table_Delimited = etree.SubElement(File_Area_Observational, 'Table_Delimited')
    name = etree.SubElement(Table_Delimited, 'name')
    name.text = '____'
    local_identifier = etree.SubElement(Table_Delimited, 'local_identifier')
    local_identifier.text = '____'
    offset = etree.SubElement(Table_Delimited, 'offset', unit="byte")
    offset.text = '____'
    parsing_standard_id = etree.SubElement(Table_Delimited, 'parsing_standard_id')
    parsing_standard_id.text = 'PDS DSV 1'
    description = etree.SubElement(Table_Delimited, 'description')
    description.text = '____'
    records = etree.SubElement(Table_Delimited, 'records')
    records.text = '____'
    record_delimiter = etree.SubElement(Table_Delimited, 'record_delimiter')
    record_delimiter.text = 'Carriage-Return Line-Feed'
    field_delimiter = etree.SubElement(Table_Delimited, 'field_delimiter')
    field_delimiter.text = 'Comma'
    Record_Delimited = etree.SubElement(Table_Delimited, 'Record_Delimited')
    fields = etree.SubElement(Record_Delimited, 'fields')
    fields.text = str(number_of_fields)
    groups = etree.SubElement(Record_Delimited, 'groups')
    groups.text = '0'
      
    #           a. Create Field Delimited for each field
    for number in range(number_of_fields):
        Field_Delimited = etree.SubElement(Record_Delimited, 'Field_Delimited')
        name_fd = etree.SubElement(Field_Delimited, 'name')
        name_fd.text = '____'
        field_number = etree.SubElement(Field_Delimited, 'field_number')
        field_number.text = '____'
        data_type_tag = etree.SubElement(Field_Delimited, 'data_type')
        data_type_tag.text = '____'
        description = etree.SubElement(Field_Delimited, 'description')
        description.text = '____'
    

    #     7. Write Product_Bundle to file in User Bundle Directory
    label = '{0}.xml'.format(the_name)
    label_path = os.path.join(data_type_path, label)
    label = open(label_path, 'w+')
    tree = etree.tostring(Product_Observational, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(tree)
    label.close()

    if data_type == 'calibrated':
        # Create Calibrated Model object
        calibrated = CalibratedForm().save(commit=False)
        calibrated.name = the_name
        calibrated.title = the_title
        calibrated.bundle = bundle
        calibrated.save()

    if data_type == 'derived':
        # Create Derived Model Object
        derived = DerivedForm().save(commit=False)
        derived.name = the_name
        derived.title = the_title
        derived.bundle = bundle
        derived.save()

    if data_type == 'raw':
        # Create Derived Model Object
        derived = RawForm().save(commit=False)
        derived.name = the_name
        derived.title = the_title
        derived.bundle = bundle
        derived.save()

    if data_type == 'reduced':
        # Create Derived Model Object
        derived = ReducedForm().save(commit=False)
        derived.name = the_name
        derived.title = the_title
        derived.bundle = bundle
        derived.save()



def DataTemplate(data_type, form, bundle, number_of_fields):

    # Navigate to data directory
    data_directory = os.path.join(bundle.directory, data_type)
    

    if form.cleaned_data['template'] == 'Table_Character_Delimited':
        # Add table character delimited template label to data directory

        #    1. Declare root and namespace
        Product_Observational = etree.Element('Product_Observational', nsmap = NAMESPACE_MAP_PRODUCT_OBSERVATIONAL)

        #    2. Build children of Root
        Identification_Area = etree.SubElement(Product_Observational, 'Identification_Area')
        Observation_Area = etree.SubElement(Product_Observational, 'Observation_Area')
        Reference_List = etree.SubElement(Product_Observational, 'Reference_List')
        File_Area_Observational = etree.SubElement(Product_Observational, 'File_Area_Observational')
        File_Area_Observational_Supplemental = etree.SubElement(Product_Observational, 'File_Area_Observational_Supplemental')

        #    3. Build Identification_Area
        logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
        lid = '{0}:{1}:____'.format(bundle.lid, data_type)
        logical_identifier.text = lid
        version_id = etree.SubElement(Identification_Area, 'version_id')
        version_id.text = '1.0'
        title = etree.SubElement(Identification_Area, 'title')
        title.text = '____'
        information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
        information_model_version.text = bundle.version

        #    4. Build Observation Area
        Time_Coordinates = etree.SubElement(Observation_Area, 'Time_Coordinates')
        start_date_time = etree.SubElement(Time_Coordinates, 'start_date_time')
        start_date_time.text = '____'
        stop_date_time = etree.SubElement(Time_Coordinates, 'stop_date_time')
        stop_date_time.text = '____'
        Primary_Result_Summary = etree.SubElement(Observation_Area, 'Primary_Result_Summary')
        purpose = etree.SubElement(Primary_Result_Summary, 'purpose')
        purpose.text = 'Science'
        processing_level = etree.SubElement(Primary_Result_Summary, 'processing_level')
        processing_level.text = 'Derived'
        Science_Facets = etree.SubElement(Primary_Result_Summary, 'Science_Facets')
        domain = etree.SubElement(Science_Facets, 'domain')
        domain.text = 'Atmospheres'
        discipline_name = etree.SubElement(Science_Facets, 'discipline_name')
        discipline_name.text = 'Atmospheres'
        facet1 = etree.SubElement(Science_Facets, 'facet1')
        facet1.text = '____'

        #    5. Build File Area Observational Area
        File = etree.SubElement(File_Area_Observational, 'File')
        file_name = etree.SubElement(File, 'file_name')
        file_name.text = '____'
        local_identifier = etree.SubElement(File, 'local_identifier')
        local_identifier.text = '____'
        creation_date_time = etree.SubElement(File, 'creation_date_time')
        creation_date_time.text = 'YYYY-MM-DDThh:mm:ss'
        file_size = etree.SubElement(File, 'file_size', unit='byte')
        file_size.text = '____'
        records = etree.SubElement(File, 'records')
        records.text = '____'
        Table_Delimited = etree.SubElement(File_Area_Observational, 'Table_Delimited')
        name = etree.SubElement(Table_Delimited, 'name')
        name.text = '____'
        local_identifier = etree.SubElement(Table_Delimited, 'local_identifier')
        local_identifier.text = '____'
        offset = etree.SubElement(Table_Delimited, 'offset', unit="byte")
        offset.text = '____'
        parsing_standard_id = etree.SubElement(Table_Delimited, 'parsing_standard_id')
        parsing_standard_id.text = 'PDS DSV 1'
        description = etree.SubElement(Table_Delimited, 'description')
        description.text = '____'
        records = etree.SubElement(Table_Delimited, 'records')
        records.text = '____'
        record_delimiter = etree.SubElement(Table_Delimited, 'record_delimiter')
        record_delimiter.text = 'Carriage-Return Line-Feed'
        field_delimiter = etree.SubElement(Table_Delimited, 'field_delimiter')
        field_delimiter.text = 'Comma'
        Record_Delimited = etree.SubElement(Table_Delimited, 'Record_Delimited')
        fields = etree.SubElement(Record_Delimited, 'fields')
        fields.text = str(number_of_fields)
        groups = etree.SubElement(Record_Delimited, 'groups')
        groups.text = '0'
        
        #           a. Create Field Delimited for each field
        for number in range(number_of_fields):
            Field_Delimited = etree.SubElement(Record_Delimited, 'Field_Delimited')
            name_fd = etree.SubElement(Field_Delimited, 'name')
            name_fd.text = '____'
            field_number = etree.SubElement(Field_Delimited, 'field_number')
            field_number.text = '____'
            data_type = etree.SubElement(Field_Delimited, 'data_type')
            data_type.text = '____'
            description = etree.SubElement(Field_Delimited, 'description')
            description.text = '____'
    

        #     7. Write Product_Bundle to file in User Bundle Directory
        label = 'FIX_NAME.xml'
        label_path = os.path.join(data_directory, label)
        label = open(label_path, 'w+')
        tree = etree.tostring(Product_Observational, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(tree)
        label.close()



# - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  
# Context Information
# - -   - - Mission Search Functions   
def InstrumentHost(request, bundle, instrumenthost):

    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:


        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        root_tag = etree.QName(root)

        if root_tag.localname is 'Product_Bundle' or 'Product_Collection':
            # Locate Observing System
            Observing_System = root[1][2]

            # Add Instrument Host to Observing System
            Observing_System_Component = etree.SubElement(Observing_System, 'Observing_System_Component')
            name = etree.SubElement(Observing_System_Component, 'name')
            name.text = instrumenthost.title.title()
            insthost_type = etree.SubElement(Observing_System_Component, 'type')
            insthost_type.text = instrumenthost.type_of
            Internal_Reference = etree.SubElement(Observing_System_Component, 'Internal_Reference')
            lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
            lid_reference.text = instrumenthost.lid
            reference_type = etree.SubElement(Internal_Reference, 'reference_type')
            reference_type.text = 'is_instrument_host'

        # When the time comes, add in if tag.localname is 'Product_Document' and if tag.localname is 'Product_Collection' and use the same function to call for those.

        # Properly close file
        label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(label_tree)
        label.close()

       

def Instrument(request, bundle, instrument):

    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:


        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        root_tag = etree.QName(root)

        if root_tag.localname is 'Product_Bundle' or 'Product_Collection':
            # Locate Observing System
            Observing_System = root[1][2]

            # Add Instrument Host to Observing System
            Observing_System_Component = etree.SubElement(Observing_System, 'Observing_System_Component')
            name = etree.SubElement(Observing_System_Component, 'name')
            name.text = instrument.title.title()
            inst_type = etree.SubElement(Observing_System_Component, 'type')
            inst_type.text = instrument.type_of
            Internal_Reference = etree.SubElement(Observing_System_Component, 'Internal_Reference')
            lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
            lid_reference.text = instrument.lid
            reference_type = etree.SubElement(Internal_Reference, 'reference_type')
            reference_type.text = 'is_instrument'

        # When the time comes, add in if tag.localname is 'Product_Document' and if tag.localname is 'Product_Collection' and use the same function to call for those.

        # Properly close file
        label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(label_tree)
        label.close()

def Target(request, bundle, target):

    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:


        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        root_tag = etree.QName(root)

        if root_tag.localname is 'Product_Bundle' or 'Product_Collection':
            # Locate Observing System
            Observing_System = root[1][2]

            # Add Instrument Host to Observing System
            Observing_System_Component = etree.SubElement(Observing_System, 'Observing_System_Component')
            name = etree.SubElement(Observing_System_Component, 'name')
            name.text = target.title.title()
            targ_type = etree.SubElement(Observing_System_Component, 'type')
            targ_type.text = target.type_of
            Internal_Reference = etree.SubElement(Observing_System_Component, 'Internal_Reference')
            lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
            lid_reference.text = target.lid
            reference_type = etree.SubElement(Internal_Reference, 'reference_type')
            reference_type.text = 'is_target'

        # When the time comes, add in if tag.localname is 'Product_Document' and if tag.localname is 'Product_Collection' and use the same function to call for those.

        # Properly close file
        label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(label_tree)
        label.close()

# - -   - - Facility Search Functions  
def Facility(facility, bundle):

    # Get all xml labels in bundle directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:
        print xml_path

        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        root_tag = etree.QName(root)

        if root_tag.localname is 'Product_Bundle' or 'Product_Collection':
            # Locate Observing System
            Observing_System = root[1][2]

            # Add Facility to Observing System
            Observing_System_Component = etree.SubElement(Observing_System, 'Observing_System_Component')
            name = etree.SubElement(Observing_System_Component, 'name')
            name.text = facility.name
            facility_type = etree.SubElement(Observing_System_Component, 'type')
            facility_type.text = facility.type_of
            Internal_Reference = etree.SubElement(Observing_System_Component, 'Internal_Reference')
            lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
            lid_reference.text = facility.lid
            reference_type = etree.SubElement(Internal_Reference, 'reference_type')
            reference_type.text = 'is_facility'

        # Properly close file
        label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(label_tree)
        label.close()
            
            


# End Context Information - -   - -  - -  - -  - -  - -  - -  - -   - -  - -  - -  - -  - -  - -  - -



# ---- TEST ----
def recursive_add(request, bundle):
    random_index = random.randint(0, Joke.objects.count()-1)
    random_joke = Joke.objects.all()[random_index]

    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:
        print xml_path

        # Create Parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        Compromised_Bundle = etree.SubElement(root, 'Compromised_Bundle')
        question = etree.SubElement(Compromised_Bundle, 'question')
        question.text = random_joke.question
        answer = etree.SubElement(Compromised_Bundle, 'answer')
        answer.text = random_joke.answer 

        # Sum up the tree
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(bundle_tree)
        label.close()

 
"""
    # Make Citation_Information model object
    citation = form.save(commit=False)
    citation.product_bundle = product_bundle
    citation.save()

    # Find Product_Bundle Label
    label = product_bundle.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')

    # Locate Citation_Information in tree and edit
    root = tree.getroot()
    Citation_Information = root[0][6]
    label_file.close()
"""
    


"""
          COMMENTED OUT FOR NOW... DO NOT DELETE!!!

def Documents(request, form, bundle):
    # Find Documents directory
    bundle_dir = bundle.directory
    document_dir = os.path.join(bundle_dir, 'document')
    
    # Place number of document labels in document directory.
    number = int(form['number'].value())
    for i in range(number):                                     # CHANGE TO LIST OF FILE NAMES

        # Grow Product Document Tree
        Product_Document = etree.Element('Product_Document', nsmap=NAMESPACE_MAP)
        Identification_Area = etree.SubElement(Product_Document, 'Identification_Area')
        Reference_List = etree.SubElement(Product_Document, 'Reference_List')
        Document = etree.SubElement(Product_Document, 'Document')

        # Fill tree with current information - Identification Area
        logical_identifier = etree.SubElement(Identification_Area, 'logical_identifier')
        logical_identifier.text = 'urn:nasa:pds:{0}:{1}:{2}'.format(bundle.name, 'document', 'FIX_TITLE')
        version_id = etree.SubElement(Identification_Area, 'version_id')
        version_id.text = '1.0'
        title = etree.SubElement(Identification_Area, 'title')
        title.text = 'FIX TITLE'
        information_model_version = etree.SubElement(Identification_Area, 'information_model_version')
        information_model_version.text = bundle.version
        product_class = etree.SubElement(Identification_Area, 'product_class')
        product_class.text = 'Product_Document'
        Citation_Information = etree.SubElement(Identification_Area, 'Citation_Information')
        Modification_History = etree.SubElement(Identification_Area, 'Modification_History')


        # Fill tree with current information - Reference List
        Internal_Reference = etree.SubElement(Reference_List, 'Internal_Reference')
        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = 'urn:nasa:pds:context:instrument:_____'
        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'document_to_instrument'
        External_Reference = etree.SubElement(Reference_List, 'External_Reference')
        reference_text = etree.SubElement(External_Reference, 'reference_text')
        description = etree.SubElement(External_Reference, 'description')

        # Fill tree with current information - Document
        revision_id = etree.SubElement(Document, 'revision_id')
        revision_id.text = '1.0'
        document_name = etree.SubElement(Document, 'document_name')
        author_list = etree.SubElement(Document, 'author_list')
        copyright = etree.SubElement(Document, 'copyright')
        publication_date = etree.SubElement(Document, 'publication_date')
        publication_date.text = 'yyyy-mm-dd'
        document_editions = etree.SubElement(Document, 'document_editions')
        document_editions.text = '1'
        description = etree.SubElement(Document, 'description')
        Document_Edition = etree.SubElement(Document, 'Document_Edition')
        edition_name = etree.SubElement(Document_Edition, 'edition_name')
        language = etree.SubElement(Document_Edition, 'language')
        files = etree.SubElement(Document_Edition, 'files')
        files.text = '1'
        Document_File = etree.SubElement(Document_Edition, 'Document_File')
        file_name = etree.SubElement(Document_File, 'file_name')
        local_identifier = etree.SubElement(Document_File, 'local_identifier')
        document_standard_id = etree.SubElement(Document_File, 'document_standard_id')


        # Write Product_Document label.  
        label = 'collection_{0}_FIX_THIS.xml'.format(i)
        label_path = os.path.join(document_dir, label)
        label = open(label_path, 'w+')
        tree = etree.tostring(Product_Document, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(tree)
        label.close()
        



"""
