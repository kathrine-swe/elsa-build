# Add to chocolate.py
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


# Add to build.py
def InstrumentToAll(request, bundle, instrument):
    DEBUG = True

    if DEBUG == True:
        print 'DEBUG build.InstrumentToAll'
        print '-- bundle id: {0}'.format(bundle.id)
        print '-- bundle name: {0}'.format(bundle.name)
        print '-- bundle lid: {0}'.format(bundle.lid)
        print '-- bundle dir: {0}'.format(bundle.directory)    

    # Get all xml labels in directory.
    xml_path_list = get_xml_path(bundle.directory)

    if DEBUG == True:
        print '\n\n'
        print 'FINDING FILES IN: bundle_mock'
        for path in xml_path_list:
            print path

    for xml_path in xml_path_list:

        # Find label
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w+')

        # Locate Observing System
        root = tree.getroot()
        Observing_System = root[1][2]

        # Add instrument to observing system
        Observing_System_Component = etree.SubElement(Observing_System, 'Observing_System_Component')
        name = etree.SubElement(Observing_System_Component, 'name')
        name.text = instrument.title.title()
        inst_type = etree.SubElement(Observing_System_Component,'type')
        inst_type.text = instrument.type_of
        Internal_Reference = etree.SubElement(Observing_System_Component, 'Internal_Reference')
        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = instrument.lid
        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'is_instrument'
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(bundle_tree)
        label.close()   

def TargetToAll(request, bundle, instrument):
    DEBUG = True

    if DEBUG == True:
        print 'DEBUG build.TargetToAll'
        print '-- bundle id: {0}'.format(bundle.id)
        print '-- bundle name: {0}'.format(bundle.name)
        print '-- bundle lid: {0}'.format(bundle.lid)
        print '-- bundle dir: {0}'.format(bundle.directory)    

    # Get all xml labels in directory.
    xml_path_list = get_xml_path(bundle.directory)

    if DEBUG == True:
        print '\n\n'
        print 'FINDING FILES IN: bundle_mock'
        for path in xml_path_list:
            print path

    for xml_path in xml_path_list: 

        # Find label        
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xml_path, parser)
        label = open(xml_path, 'w+')

        # Locate Context Area
        root = tree.getroot()
        Context_Area = root[1]

        # Add Target Identification to Context Area
        Target_Identification = etree.SubElement(Context_Area, 'Target_Identification')
        name = etree.SubElement(Target_Identification, 'name')
        name.text = target.title.title()
        targ_type = etree.SubElement(Target_Identification, 'type')
        targ_type = target.type_of
        Internal_Reference = etree.SubElement(Target_Identification, 'Internal_Reference')
        lid_reference = etree.SubElement(Internal_Reference, 'lid_reference')
        lid_reference.text = target.lid
        reference_type = etree.SubElement(Internal_Reference, 'reference_type')
        reference_type.text = 'is_target'
        bundle_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label.write(bundle_tree)
        label.close()
        
