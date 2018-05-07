# Stdlib imports

# Core Django imports
from django.conf.urls import url, include

# Third-party app imports

# Imports from apps
from . import views



app_name='build'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Bundle urls
    #url(r'^(?P<pk>\d+)/$', views.BundleDetail.as_view(), name='bundle_detail'),
    url(r'^(?P<pk_bundle>\d+)/$', views.bundle_detail, name='bundle_detail'), # Secure
    url(r'^(?P<pk_bundle>\d+)/confirm_delete/$', views.bundle_delete, name='bundle_delete'), # Secure
    url(r'^success_delete/$', views.bundle_success_delete, name='bundle_success_delete'),
    url(r'^(?P<pk_bundle>\d+)/download/$', views.bundle_download, name='bundle_download'), # Need to secure.


    # Product_Bundle urls
    url(r'^(?P<pk_bundle>\d+)/product_bundle/identification_area/alias/$', views.alias, name='alias'),
    url(r'^(?P<pk_bundle>\d+)/product_bundle/identification_area/citation_information/$', views.citation_information, name='citation_information'),


    # Document
    url(r'^(?P<pk_bundle>\d+)/document/$', views.document, name='document'),
    url(r'^(?P<pk_bundle>\d+)/document/(?P<pk_document>\d+)/edit/$', views.document_edit, name='document_edit'),


    # Context
    url(r'^(?P<pk_bundle>\d+)/context/$', views.context, name='context'),
    url(r'^(?P<pk_bundle>\d+)/contextquery/search/mission/$', views.context_search, name='context_search'),  # EVENTUALLY need to change view and name to context_search_mission
    url(r'^(?P<pk_bundle>\d+)/contextquery/search/mission/(?P<pk_instrument_host>\d+)/$', views.instrument_host_detail, name='instrument_host_detail'),
    url(r'^(?P<pk_bundle>\d+)/contextquery/search/mission/(?P<pk_instrument_host>\d+)/instrument/(?P<pk_instrument>\d+)/confirm_delete/$', views.instrument_delete, name='instrument_delete'),
    url(r'^(?P<pk_bundle>\d+)/contextquery/search/facility/$', views.context_search_facility, name='context_search_facility'),

    # XML_Schema

    # Data
    url(r'^(?P<pk_bundle>\d+)/data/$', views.data, name='data'),
    url(r'^(?P<pk_bundle>\d+)/data/(?P<pk_data>\d+)/$', views.data_template, name='data_template'),




    # Bundle urls not in use
    url(r'^(?P<pk_bundle>\d+)/editor/$', views.bundle_editor, name='product_bundle_editor'),

    # Product_Bundle urls not in use
    url(r'^(?P<pk_bundle>\d+)/product_bundle/identification_area/alias/(?P<pk_alias>\d+)/delete/$', views.alias_delete, name='alias_delete'),
    url(r'^(?P<pk_bundle>\d+)/product_bundle/identification_area/citation_information/(<?P<pk_citation_information>\d+)/delete/$', views.citation_information, name='citation_information'),


    # Product Bundle urls not in use



    # Product Collection urls not in use



    # TEST
    url(r'^some_xml/$', views.some_xml, name='some_xml'),
    url(r'^(?P<pk_bundle>\d+)/test/$', views.test, name='test'),
    url(r'^(?P<pk_bundle>\d+)/test/recursive_add$', views.recursive_add, name='recursive_add'),
]
