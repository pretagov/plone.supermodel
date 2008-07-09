from zope.interface import Interface, implements
from zope.component import adapts, getUtilitiesFor

from zope.schema.interfaces import IField
from zope.schema import getFieldNamesInOrder

from zope.component import queryUtility

from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import IFieldMetadataHandler

from plone.supermodel.interfaces import XML_NAMESPACE

from plone.supermodel.model import FIELDSETS_KEY

from elementtree import ElementTree

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def pretty_xml(tree):
    indent(tree)
    return ElementTree.tostring(tree)

class IFieldNameExtractor(Interface):
    """Adapter to determine the canonical name of a field
    """
    
    def __call__():
        """Return the name of the adapted field
        """

class DefaultFieldNameExtractor(object):
    """Extract a name
    """
    implements(IFieldNameExtractor)
    adapts(IField)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        field_module = self.context.__class__.__module__
        
        # workaround for the fact that some fields are defined in one
        # module, but commonly used from zope.schema.*

        if field_module.startswith('zope.schema._bootstrapfields'):
            field_module = field_module.replace("._bootstrapfields", "")
        elif field_module.startswith('zope.schema._field'):
            field_module = field_module.replace("._field", "")
        
        return "%s.%s" % (field_module, self.context.__class__.__name__,)

# Algorithm

def serialize(model):
    
    handlers = {}
    schema_metadata_handlers = tuple(getUtilitiesFor(ISchemaMetadataHandler))
    field_metadata_handlers = tuple(getUtilitiesFor(IFieldMetadataHandler))

    xml = ElementTree.Element('model')
    xml.set('xmlns', XML_NAMESPACE)
    
    # Let utilities indicate which namespace they prefer.

    # XXX: This is manipulating a global - it's probably safe, though,
    # since we only add new items, and only add them if they don't conflict
    
    used_prefixes = set(ElementTree._namespace_map.values())
    for name, handler in schema_metadata_handlers + field_metadata_handlers:
        namespace, prefix = handler.namespace, handler.prefix
        if namespace is not None and prefix is not None \
                and prefix not in used_prefixes and namespace not in ElementTree._namespace_map:
            used_prefixes.add(prefix)
            ElementTree._namespace_map[namespace] = prefix
    
    def write_field(field, parent_element):
        name_extractor = IFieldNameExtractor(field)
        field_type = name_extractor()
        handler = handlers.get(field_type, None)
        if handler is None:
            handler = handlers[field_type] = queryUtility(IFieldExportImportHandler, name=field_type)
            if handler is None:
                raise ValueError("Field type %s specified for field %s is not supported" % (field_type, field_name,))
        field_element = handler.write(field, field_name, field_type)
        if field_element is not None:
            parent_element.append(field_element)
            
            for handler_name, metadata_handler in field_metadata_handlers:
                metadata_handler.write(field_element, schema, field)
    
    for schema_name, schema in model.schemata.items():
        
        fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])
        
        fieldset_fields = set()
        for fieldset in fieldsets:
            fieldset_fields.update(fieldset.fields)
        
        non_fieldset_fields = [name for name in getFieldNamesInOrder(schema) 
                                if name not in fieldset_fields]
        
        
        schema_element = ElementTree.Element('schema')
        if schema_name:
            schema_element.set('name', schema_name)
        
        for field_name in non_fieldset_fields:
            field = schema[field_name]
            write_field(field, schema_element)
        
        for fieldset in fieldsets:
            
            fieldset_element = ElementTree.Element('fieldset')
            fieldset_element.set('name', fieldset.__name__)
            if fieldset.label:
                fieldset_element.set('label', fieldset.label)
            if fieldset.description:
                fieldset_element.set('description', fieldset.description)
            
            for field_name in fieldset.fields:
                field = schema[field_name]
                write_field(field, fieldset_element)
        
            schema_element.append(fieldset_element)
        
        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.write(schema_element, schema)
        
        xml.append(schema_element)

    return pretty_xml(xml)

__all__ = ('serialize',)