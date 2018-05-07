#

# Stdlib imports
# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from .forms import * 
from .models import *
from . import build, remove, crawl
from chocolate import make_tarfile, replace_all, get_xml_path
import os

# Create your views here.
# For more information on a Django View, please see the Django Docs.


# The bundle_detail view is the page that details a specific bundle.
@login_required
def bundle_detail(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    bundle_user = bundle.user


    print 'BEGIN bundle_detail VIEW'
    if request.user == bundle.user:
        context_dict = {
            'bundle':bundle,
            'alias_list':Alias.objects.filter(bundle=bundle),
            'citation_information':Citation_Information.objects.filter(bundle=bundle),
        }
        return render(request, 'build/bundle/detail.html', context_dict)

    else:
        return redirect('main:restricted_access')

# The bundle_download view is not a page.  When a user chooses to download a bundle, this 'view' manifests and begins the downloading process.
def bundle_download(request, pk_bundle):
    # Grab bundle directory
    bundle = Bundle.objects.get(pk=pk_bundle)

    print 'BEGIN bundle_download VIEW'
    print 'Username: {}'.format(request.user.username)
    print 'Bundle directory name: {}'.format(bundle.get_name_directory())
    print 'Current working directory: {}'.format(os.getcwd())
    print settings.TEMPORARY_DIR
    print settings.ARCHIVE_DIR

    # Make tarfile
    #    Note: This does not run in build directory, it runs in elsa directory.  
    #          Uncomment print os.getcwd() if you need the directory to see for yourself.
    tar_bundle_dir = '{}.tar.gz'.format(bundle.get_name_directory())
    temp_dir = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)
    source_dir = os.path.join(settings.ARCHIVE_DIR, request.user.username)
    source_dir = os.path.join(source_dir, bundle.get_name_directory())
    make_tarfile(temp_dir, source_dir)

    # Testing.  See if simply bundle directory will download.
    # Once finished, make directory a tarfile and then download.
    file_path = os.path.join(settings.TEMPORARY_DIR, tar_bundle_dir)


    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-tar")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    return HttpResponse("Download did not work.")

# The bundle_delete view is the page a user sees once they select the delete bundle button.  This view gives the user an option to confirm or take back their choice.  This view could be improved upon.
@login_required
def bundle_delete(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    user = bundle.user
    delete_bundle_form = ConfirmForm(request.POST or None)

    context_dict = {}
    context_dict['bundle'] = bundle
    context_dict['user'] = user
    context_dict['delete_bundle_form'] = delete_bundle_form
    context_dict['decision'] = 'has yet to have the chance to be'

    # Secure:  If current user is the user associated with the bundle, then...
    if request.user == user:
        if delete_bundle_form.is_valid():
            print 'form is valid'
            print 'decision: {}'.format(delete_bundle_form.cleaned_data["decision"])
            decision = delete_bundle_form.cleaned_data['decision']
            if decision == 'Yes':
                context_dict['decision'] = 'was'
                success_status = remove.bundle_dir_and_model(bundle, user)
                if success_status:
                    return redirect('../../success_delete/')


            if decision == 'No':
                # Go back to bundle page
                context_dict['decision'] = 'was not'

        return render(request, 'build/bundle/confirm_delete.html', context_dict)

    # Secure: Current user is not the user associated with the bundle, so...
    else:
        return redirect('main:restricted_access')


# This view goes hand in hand with bundle_delete.  This view might not be necessary if the above view (bundle_delete) is improved upon.
@login_required
def bundle_success_delete(request):
    return render(request, 'build/bundle/success_delete.html', {})



# document view allows user to create a Document model object by filling out a DocumentForm.  If the form is valid, then we do all of our logic for Document found in the build file.
@login_required
def document(request, pk_bundle):
    context_dict = {}
    bundle = Bundle.objects.get(pk=pk_bundle)

    form_document = DocumentForm(request.POST, request.FILES or None)

    # Secure: If current user is the user associated with the bundle, then...
    if request.user == bundle.user:
        if form_document.is_valid():

            # Build Document Label in Document Directory
            build.Document(request, form_document, bundle)

            # Update context_dict
            context_dict['bundle'] = bundle
            context_dict['form_document'] = form_document
            context_dict['documents'] = Document.objects.filter(bundle=bundle)

            return render(request, 'build/document/add.html', context_dict)

        context_dict['bundle'] = bundle
        context_dict['form_document'] = form_document
        context_dict['documents'] = Document.objects.filter(bundle=bundle)

        return render(request, 'build/document/add.html', context_dict)

    # Secure: Current user is not the user associated with the bundle, so...
    else:
        return redirect('main:restricted_access')




@login_required
def index(request): 
    print 'DEBUG START --------------------'
    form_bundle = BundleForm(request.POST or None)
    form_collections = CollectionsForm(request.POST or None)
    context_dict = {
        'form_bundle':form_bundle,
        'form_collections':form_collections,
        'user':request.user,
    }

    if form_bundle.is_valid() and form_collections.is_valid():
        print 'all forms valid'

        # Check Uniqueness
        bundle_name = form_bundle.cleaned_data['name']
        bundle_user = request.user
        bundle_count = Bundle.objects.filter(name=bundle_name, user=bundle_user).count()
        # If user and bundle name are unique, then...
        if bundle_count == 0:

            # Build Bundle model object and begin PDS4 Compliant Bundle directory in User Directory.
            # This Bundle Directory will contain a Product_Bundle label.
            bundle = build.Bundle(request, form_bundle)
            
            # Build Collections model object and continue with PDS4 compliant Bundle directory in User 
            # directory.  Bundle directory will contain a collection folder for each collection and a
            # Product_Collection label.            
            build.Collections(request, form_collections, bundle)
            
            # Further develop context_dict entries for templates            
            context_dict['Bundle'] = bundle
            context_dict['Product_Bundle'] = Product_Bundle.objects.get(bundle=bundle)
            context_dict['Product_Collection_Set'] = Product_Collection.objects.filter(bundle=bundle)

            return render(request, 'build/two.html', context_dict)


# ---- CHECK THIS OUT ----
        # If user has a bundle with that name, then...
        # !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !! --- FIX ME --- !!
        # This should just simply present as an error on screen.  It does when you add a document.
        #else:    
         #   return HttpResponse("You already have a bundle with that name. Please press back on your browser and provide a new name.")
# ---- END CHECK ----            

    return render(request, 'build/index.html', context_dict)


########## NEEDS TO BE REMOVED ###########
@login_required
def bundle_editor(request, pk_bundle):

    context_dict = {}
    bundle = Bundle.objects.get(pk=pk_bundle)
    context_dict['bundle'] = bundle
    context_dict['alias_list'] = Alias.objects.filter(bundle=bundle)
    context_dict['citation_information_list'] = Citation_Information.objects.filter(bundle=bundle)
    
    # Secure: If current user is bundle user, then...
    if request.user == bundle.user:
        return render(request, 'build/product_bundle/editor.html', context_dict)

    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')
######## FIND IN URLS AND TEMPLATES AND ALL OTHER PLACES BEFORE DELETION ##############


# alias view allows user to add an alias to their bundle by filling out an AliasForm and creating an Alias model object.
@login_required
def alias(request, pk_bundle):
    context_dict = {}
    bundle = Bundle.objects.get(pk=pk_bundle)
    product_bundle = Product_Bundle.objects.get(bundle=bundle)
    form_alias = AliasForm(request.POST or None)

    # Secure: If current user is bundle user, then...
    if request.user == bundle.user:
        if form_alias.is_valid():
            
            build.Alias(form_alias, product_bundle)

        context_dict['bundle'] = bundle
        context_dict['form_alias'] = form_alias
        context_dict['alias_list'] = Alias.objects.filter(bundle=bundle)

        return render(request, 'build/alias/add.html', context_dict)

    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')

# alias delete allows the user to delete an alias from their bundle and the associated alias model object
@login_required
def alias_delete(request, pk_bundle, pk_alias):
    context_dict = {}
    alias = Alias.objects.get(pk=pk_alias)
    bundle = Bundle.objects.get(pk=pk_bundle)
    product_bundle = Product_Bundle.objects.get(bundle=bundle)

    # Secure: If current user is bundle user, then...
    if request.user == bundle.user:

        build.AliasRemove(alias, product_bundle)

        context_dict['bundle'] = bundle
        context_dict['form_alias'] = AliasForm(request.POST or None)
        context_dict['alias_list'] = Alias.objects.filter(bundle=bundle)

        return render(request, 'build/alias/add.html', context_dict)

    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')


@login_required
def citation_information(request, pk_bundle):
    context_dict = {}
    bundle = Bundle.objects.get(pk=pk_bundle)

    if request.user == bundle.user:
        form_citation_information = CitationInformationForm(request.POST or None)

        if form_citation_information.is_valid():
            print 'form is valid'
            number_of_cites_associated_with_bundle = Citation_Information.objects.filter(bundle=bundle).count()
            if number_of_cites_associated_with_bundle == 0:
                build.CitationInformation(form_citation_information, bundle)
            else:
                return HttpResponse('Cannot add more than one citation to a bundle.')

        context_dict['bundle'] = bundle
        context_dict['form_citation_information'] = form_citation_information
        context_dict['citation_information_list'] = Citation_Information.objects.filter(bundle=bundle) 
        return render(request, 'build/citation_information/add.html', context_dict)

    else:
        return redirect('main:restricted_access')

@login_required
def context(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)

    if request.user == bundle.user:
        context_dict = {}
        context_dict['bundle'] = Bundle.objects.get(pk=pk_bundle)
        context_dict['instrument_list'] = Instrument.objects.filter(bundle=context_dict['bundle'])
        context_dict['target_list'] = Target.objects.filter(bundle=context_dict['bundle'])
        return render(request, 'build/context/query.html', context_dict)

    else:
        return redirect('main:restricted_access')


@login_required
def data(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    form_data = DataForm(request.POST or None)

    if request.user == bundle.user:
        context_dict = {
            'bundle':bundle,
            'form_data':form_data,
            'data_set':Data.objects.filter(bundle=bundle),
        }

        if form_data.is_valid():
            new_data_set = build.DataSet(form_data, bundle)
            context_dict['new_data_set'] = new_data_set
            
        else:
            print 'form not valid'        
        return render(request, 'build/data/index.html', context_dict)
    else:
        return redirect('main:restricted_access')


@login_required
def data_template(request, pk_bundle, pk_data):
    bundle = Bundle.objects.get(pk=pk_bundle)
    data = Data.objects.get(pk=pk_data)
    DATA_STRUCTURE_CHOICES = ['array', 'table', 'parsable_byte_stream', 'encoded_byte_stream',]


    if request.user == bundle.user:
        context_dict = {
            'bundle':bundle,
            'data':data,
        }
        if data.structure == 'array':
            form_array = ArrayForm(request.POST or None)
            context_dict['form_data_structure'] = form_array
        if data.structure == 'table':
            form_table = TableForm(request.POST or None)
            context_dict['form_data_structure'] = form_table
            if form_table.is_valid():
                build.DataTemplate(form_table, data)
        if data.structure == 'parsable_byte_stream':
            context_dict['form_data_structure'] = 'This part of ELSA is a work in progress.'
        if data.structure == 'encoded_byte_stream':
            context_dict['form_data_structure'] = 'This part of ELSA is a work in progress.'
        return render(request, 'build/data/structure.html', context_dict)

    else:
        return redirect('main:restricted_access')









@login_required
def product_collection_editor(request, pk):

    context_dict = {}
    product_collection = Product_Collection.objects.get(pk=pk)
    context_dict['bundle'] = Bundle.objects.get(product_collection=pk)
    context_dict['product_collection'] = product_collection

    # Security: If current user is bundle user
    if request.user == bundle.user:
        return render(request, 'build/product_collection/editor.html', context_dict)

    # Security: current user is not bundle user
    else:
        return redirect('main:restricted_access')





@login_required
def document_edit(request, pk_bundle, pk_document):

    bundle = Bundle.objects.get(pk=pk_bundle)

    if request.user == bundle.user:
        document = Document.objects.get(pk=pk_document)
        form_document_edit = DocumentEditForm(request.POST or None)
        context_dict = {
            'bundle':bundle,
            'document':document,
            'documents': Document.objects.filter(bundle=bundle),
            'form_document_edit':form_document_edit,
        }
        if form_document_edit.is_valid():
            # Edit the document and collection label.

            pass
        return render(request, 'build/document/edit.html', context_dict)

    else:
        return redirect('main:restricted_access')



#  LOOK INTO DELETION OF VIEWERS ---- Date: Dec 2017
@login_required
def product_document_viewer(request, pk_product_document):
    product_document = Product_Document.objects.get(pk=pk_product_document)
    bundle = product_document.bundle

    if request.user == bundle.user:
        xml_data = open(product_document.label, 'rb').read()
        return HttpResponse(xml_data, content_type='text/xml')

    else:
        return redirect('main:restricted_access')




@login_required
def context_search(request, pk_bundle):
    form_mission = MissionForm(request.POST or None)
    bundle = Bundle.objects.get(pk=pk_bundle)
    context_dict = {}
    context_dict['bundle'] = bundle
    context_dict['form_mission'] = form_mission
    
    # Secure: If current user is bundle user, then...
    if request.user == bundle.user:
        if form_mission.is_valid():
            print 'form_mission is valid'

            # Get or Create Mission Model
            name = form_mission.cleaned_data['name']
            print 'Name entered is {}'.format(name)
            if name:
                mission, created = Mission.objects.get_or_create(name=name)
                context_dict['Mission'] = mission
                title_mission = mission.name.title()
                title_mission = replace_all(title_mission, '_', ' ')
                context_dict['title_mission'] = title_mission

                if created:
                    # Crawl Starbase investigation given mission name
                    context_dict = crawl.investigation(context_dict)
                    context_dict = crawl.instrument_host(context_dict)
                else:
                    # Mission Model exists so we simply get the corresponding instrument hosts
                    # to present as choices for the user.
                    instrument_host_list = InstrumentHost.objects.filter(mission=mission)
                    print 'instrument host list: '
                    for host in instrument_host_list:
                        print host
                    context_dict['instrument_host_list'] = instrument_host_list

               # Note:  Context search is where a user selects the instrument host.  You may or may not be looking to find where ELSA adds the instrument host information to a bundle.  This information however, is not found here.  The reason the instrument host is not added here is because a user may simply be searching through instrument hosts for instruments and targets.  Once a user selects instruments and targets, we can simply add the instrument host then to ensure the intended result for the user.  Thus, if you're looking for where ELSA adds the instrument host information, go to instrument_host_detail where ELSA adds the instrument host, instrument(s), and target(s).

            return render(request, 'build/context/search/instrument_host.html', context_dict)        
        return render(request, 'build/context/search/search.html', context_dict)

    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')


@login_required
def context_search_facility(request, pk_bundle):
    form_facility = FacilityForm(request.POST or None)
    bundle = Bundle.objects.get(pk=pk_bundle)
    context_dict = {}
    context_dict['bundle'] = bundle
    context_dict['form_facility'] = form_facility
    context_dict['facility_list'] = Facility.objects.filter(bundle=bundle)

    # Secure: If current user is bundle user, then... we're good
    if request.user == bundle.user:
        if form_facility.is_valid():

            # Then we need to build the facility part of our labels.
            # 1. Get facility model object (Facility model objects are created in crawl.facility_list)
            title = form_facility.cleaned_data['title']
            title = dict(form_facility.fields['title'].choices)[title]
            if title:

                # 1. Get facility model object
                print title
                facility = Facility.objects.get(title=title)

                # 2. Link facility model object to user's bundle model object
                facility.bundle.add(bundle)
                facility.save()

                # 3. Build facility components of labels.
                build.Facility(facility, bundle)
        
            
        return render(request, 'build/context/facility/facility.html', context_dict)
    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')


@login_required
def instrument_host_detail(request, pk_bundle, pk_instrument_host):
    form_choose_instruments = ChooseInstrumentsForm(pk_instrument_host=pk_instrument_host)
    form_choose_targets = ChooseTargetsForm(pk_instrument_host=pk_instrument_host)
    bundle = Bundle.objects.get(pk=pk_bundle)
    print 'BUNDLE: {}'.format(bundle)
    context_dict = {}

    # Secure: If current user is bundle user, then...
    if request.user == bundle.user:
        if request.method == 'POST':
            form_choose_instruments = ChooseInstrumentsForm(request.POST, pk_instrument_host=pk_instrument_host)
            form_choose_targets = ChooseTargetsForm(request.POST, pk_instrument_host=pk_instrument_host)

            if form_choose_instruments.is_valid() and form_choose_targets.is_valid():

                # Add Instrument Host
                instrumenthost = InstrumentHost.objects.get(pk=pk_instrument_host)
                build.InstrumentHost(request, bundle, instrumenthost)

                # Add Instrument(s)
                for instrument_name in form_choose_instruments.cleaned_data['instrument_list']:

                    # Link instrument to User's Bundle
                    instrument = Instrument.objects.get(title=instrument_name, instrument_host=instrumenthost)
                    instrument.bundle.add(bundle)
    
                    # Add instrument to Product_Bundle, Context's Product_Collection...
                    build.Instrument(request, bundle, instrument)

                # Add Target(s)
                for target_name in form_choose_targets.cleaned_data['target_list']:
    
                    # Link target to User's Bundle
                    target = Target.objects.get(title=target_name, instrument_host=pk_instrument_host)
                    target.bundle.add(bundle)

                    # Add target to Product_Bundle, Context's Product_Collection...
                    build.Target(request, bundle, target)



        context_dict['bundle'] = bundle
        context_dict['instrument_host'] = InstrumentHost.objects.get(pk=pk_instrument_host)
        context_dict['form_choose_instruments'] = form_choose_instruments
        context_dict['form_choose_targets'] = form_choose_targets
        context_dict['instrument_list'] = Instrument.objects.filter(bundle=bundle)
        context_dict['target_list'] = Target.objects.filter(bundle=bundle)
    
        return render(request, 'build/context/search/instrument_host_detail.html', context_dict)

    # Secure: Current user is not bundle user
    else:
        return redirect('main:restricted_access')



@login_required
def instrument_delete(request, pk_bundle, pk_instrument_host, pk_instrument):
    pass

@login_required
def target_delete(request, pk_bundle, pk_instrument_host, pk_target):
    pass








# ---- BELOW ARE TEST VIEWS ----
# Works
def some_xml(request):
    my_path = os.path.join(settings.MEDIA_DIR, '6')
    my_path = os.path.join(my_path, 'hummus_bundle')
    my_path = os.path.join(my_path, 'bundle_hummus.xml')
    xml_data = open(my_path, 'rb').read()
    return HttpResponse(xml_data, content_type='text/xml')

def test(request, pk_bundle):
    return render(request, 'test/test.html', {'bundle':Bundle.objects.get(pk=pk_bundle)})


def recursive_add(request, pk_bundle):
    bundle = Bundle.objects.get(pk=pk_bundle)
    print 'Bundle: {}'.format(bundle)
    print 'User: {}'.format(bundle.user)
    print '\n\n'

    # Do Stuff
    build.recursive_add(request, bundle)

    return HttpResponse("The deal has been made.")










# TOMORROW --- Look Here.
# https://stackoverflow.com/questions/29714763/django-check-if-checkbox-is-selected
