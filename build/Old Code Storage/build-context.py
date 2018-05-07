def Instrument(request, bundle, instrument):
    print 'DEBUG build.Instrument'
    print '-- bundle id: {0}'.format(bundle.id)
    print '-- bundle name: {0}'.format(bundle.name)
    print '-- bundle lid: {0}'.format(bundle.lid)
    print '-- bundle dir: {0}'.format(bundle.directory)

    # Find Product_Bundle Label
    product_bundle_object = Product_Bundle.objects.get(bundle=bundle)
    label = product_bundle_object.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')

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
    label_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
    label_file.write(label_tree)
    label_file.close()

    # Add instrument to each Product_Collection label
    product_collection_set = Product_Collection.objects.filter(bundle=bundle)
    for product_collection in product_collection_set:

        # Find Context's Product_Collection Label
        label = product_collection.label
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(label, parser)
        label_file = open(label, 'w+')

        # Locate Observing System
        root = tree.getroot()
        Observing_System = root[1][2]

        # Add instrument to observing system
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
        collection_tree = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        label_file.write(collection_tree)
        label_file.close()

def Instrument_Want(request, bundle, instrument):
    print 'DEBUG build.Instrument'
    print '-- bundle id: {0}'.format(bundle.id)
    print '-- bundle name: {0}'.format(bundle.name)
    print '-- bundle lid: {0}'.format(bundle.lid)
    print '-- bundle dir: {0}'.format(bundle.directory)

    # Get all xml labels in directory
    xml_path_list = get_xml_path(bundle.directory)

    # Traverse labels
    for xml_path in xml_path_list:
        print xml_path

        # Create Parser
        #parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        #tree = etree.parse(xml_path, parser)
        #label = open(xml_path, 'w')

        # Do what needs to be done
        root = tree.getroot()
        # if data template, browse do nothing
        # else, everything has a root[0][1] as observing_system_component


    
def Target(request, bundle, target):
    print 'DEBUG build.Instrument'
    print '-- bundle id: {0}'.format(bundle.id)
    print '-- bundle name: {0}'.format(bundle.name)
    print '-- bundle lid: {0}'.format(bundle.lid)
    print '-- bundle dir: {0}'.format(bundle.directory)

    # Find Product_Bundle Label
    product_bundle_object = Product_Bundle.objects.get(bundle=bundle)
    label = product_bundle_object.label
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    tree = etree.parse(label, parser)
    label_file = open(label, 'w+')

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
    label_file.write(bundle_tree)
    label_file.close()

    # Add target to each Product_Collection label
    product_collection_set = Product_Collection.objects.filter(bundle=bundle)
    for product_collection in product_collection_set:

        # Find Context's Product_Collection Label
        label = product_collection.label
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        tree = etree.parse(label, parser)
        label_file = open(label, 'w+')

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
        label_file.write(bundle_tree)
        label_file.close()

