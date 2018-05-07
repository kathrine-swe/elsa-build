# remove.py
# PieceOfKayk

# remove is responsible for deleting python model objects from the database while synonymously removing the corresponding data from the user's directory.

import shutil
import os
from .models import Bundle


# remove.bundle removes the bundle directory and all of its contents from the user's directory.  If the directory was removed, then the bundle model object is deleted from the ELSA database.  The function then returns status true if everything was removed correctly.
def bundle_dir_and_model(bundle, user):

    # Declarations    
    debug_status = True
    complete_removal_status = False
    directory_removal_status = False
    model_removal_status = False

    
    if debug_status == True:
        print '-----------------------------'
        print 'remove.bundle_dir_and_model\n\n'
        print 'bundle_directory: {}'.format(bundle.directory)

    if os.path.isdir(bundle.directory):

        if debug_status == True:
            print 'os.path.isdir(bundle.directory): True'

        shutil.rmtree(bundle.directory)
        if not os.path.isdir(bundle.directory):
            directory_removal_status = True

    if Bundle.objects.filter(name=bundle.name, user=user).count() > 0: # Should be no more than one
        b = Bundle.objects.filter(name=bundle.name, user=user)
        b.delete()
        if Bundle.objects.filter(name=bundle.name, user=user).count() == 0:
            model_removal_status = True

    if directory_removal_status and model_removal_status:
        complete_removal_status = True
            

    return complete_removal_status

# remove.alias removes the alias tag and all children of alias from all labels containing alias.  If the alias was removed, then the alias model object is deleted from the ELSA database.  The function then returns complete_removal_status as true if everything was removed correctly.
def alias(bundle, alias, user):
    
    # Declarations
    complete_removal_status = False
    label_removal_status = False
    model_removal_status = False

    # Get Product_Bundle label and Open label -- the only label with Alias
    product_bundle = Product_Bundle.objects.get(bundle=bundle)
    label = product_bundle.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')

    # Get root
    root = tree.getroot()
    Alias_List = root[0][5]
    list_of_alias_tags_in_Alias_List = AliasList.getchildren()

    # Traverse through Alias to find the Alias requested to be deleted.
    for alias in list_of_alias_tags_in_Alias_List:

        # Get children of alias--alternate_id, alternate_title, comment.
        children_of_alias = alias.getchildren()

        for child in children_of_alias:
            child_tag = etree.QName(child)

            # If the text matches, then all of Alias needs to be removed.  Hmmm, how to do that?  I don't know just yet... So we pass.
            if child_tag.localname is 'alternate_id' and child.text is alias.alternate_id:
                pass
            if child_tag.localname is 'alternate_title' and child.text is alias.alternate_title:
                pass
            if child_tag.localname is 'comment' and child.text is alias.comment:
                pass        
    
    # Properly close label
    label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label.write(label_tree)
    label.close()
    
        
    
    
