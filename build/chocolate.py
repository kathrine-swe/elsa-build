# chocolate.py
# Elsa is very fond of chocolate.  Despite being locked in her room, Elsa ate all the triple-double-fudge
# sundaes she wanted.  Therefore, this document contains all of the functions that aren't a necessity
# for Elsa, yet make Elsa's life better.


# imports for MediaInfo and MediaObject
from django.template import Context, loader
from lxml import etree
from xml.dom import minidom
import sys
import urllib2
import os
import tarfile

# --- Useful functions ---
#   FIRST:  Do you know what a Python function is?  If not, check out the following resources.
#             1. A brief introduction to what a Python function is.
#                https://en.wikibooks.org/wiki/Python_Programming/Functions
#             2. A short exercise to show you how a function works. (Requires Codeacademy account)
#                https://www.codecademy.com/courses/learn-python/lessons/functions/exercises/min?action=lesson_resume


# A python function 


# replaceAll replaces all of a given instance of s with t
# python's replace(s,t) only replaces one instance of s with t
def replace_all( r, s, t ):
    while( s in r ):
        r = r.replace( s, t)
    return r

# title_case takes in a string r.  Not only does title case use the python function title() to capitalize the first letter of each word, this title case function removes any underscores and replaces it with spaces.
def title_case(r):
    r = replace_all( r, '_', ' ')
    r = r.title()
    return r

# lid_case is essentially the opposite of title case (almost).  We ensure all letters are in lowercase and replace any spaces with underscores.
def lid_case(r):
    r = replace_all( r, ' ', '_')
    r = r.lower()
    return r


# make_directory makes a directory at the given path.  If the path already exists, it does nothing.  Without having the second condition, our page would throw an error if the path already exists.  
def make_directory(path):
    try:
        os.mkdir(path)
    except OSError as e:   
        if e.errno ==17:
            # Dir already exists.
            # Elsa will use the existing directory
            pass


# I'm looking back at this (Jan 2018, k) and I'm not sure why I have a seperate function for this or where its used.  I need to check it out.
def make_data_type_directory(path, data_type, bundle):
    try:
        os.mkdir(path)
        return True

    except OSError as e:   
        if e.errno ==17:
            # Dir already exists.
            # Elsa will use the existing directory
            return False

# make_tarfile creates a tarfile with name output_filename, and of a given directory, source_directory.
def make_tarfile(output_filename, source_directory):
    with tarfile.open(output_filename, 'w:gz') as tar:
        print 'Basename: {}'.format(os.path.basename(source_directory))
        tar.add(source_directory, arcname=os.path.basename(source_directory))

# print_file_path finds the xml labels in a directory and prints the paths for the xml labels.  This function does not distinguish between the content, it simply grabs all .xml files, which in our case should only be labels.
def print_file_path(directory):
    file_path_list = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".xml"):
                print(os.path.join(dirpath, filename))

def get_xml_path(directory):
    xml_path_list = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".xml"):
                xml_path = os.path.join(dirpath, filename)
                xml_path_list.append(xml_path)

    return xml_path_list


def is_product_bundle(xml_path):
    base = os.path.basename(xml_path)

    if base.startswith('bundle'):
        return True
    else:
        return False

def is_product_collection(xml_path):
    base = os.path.basename(xml_path)

    if base.startswith('collection'):
        return True
    else:
        return False

def choices( type_of_choice ):
    if type_of_choice is 'mission':
        # then the choice function returns a list of the most up-to-date missions listed in Starbase.
        # 1. Crawl to starbase.jpl.nasa.gov/pds4/context-pds4/investigation/Product/
        pass
        

# Tests
# We can test the above functions by making function calls.  To make a function call, simply state the name of the function and give it paramaters.  Por ejemplo: name_of_function(parameter1, parameter2).  When the computer reads this line, it grabs the function defined above named name_of_function.  It then passes two parameters, namely parameter1 and parameter2.  By running this script in the terminal, we can see the output of the stated function.  The output is normally whatever the function returns but this isn't always the case.  The output could also include the creation of new model objects in the database, new labels or directories in the archive, or a deletion of a model object in a directory, or a deletion of labels or directories in the archive, ... .  
is_product_bundle('/export/atmos1/htdocs/elsa/archive/test_user_01/development_test_bundle/bundle_development_test.xml')







"""
# --- Not too sure when I wrote this or why --- k
# Mapper class to map XML to a media object.
class MediaInfo(object):
    def __init__(self, el):
        self.node = el.get('node')
        self.num = el.get('num')
        self.destURI = el.find('destURI').text
        self.sourceStatus = el.find('sourceStatus').text

class MediaObject(object):
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        self.tree = etree.ElementTree(file=xmlfile)
        self.root = self.tree.getroot()
        self.sInfo = MediaInfo(self.root.find('sInfo'))

"""
