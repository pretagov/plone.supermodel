from zope.interface import Interface
from zope.interface.interfaces import IInterface
import zope.schema

# The namespace for the default supermodel schema/field parser

XML_NAMESPACE = u"http://namespaces.plone.org/supermodel/schema"

class IModel(Interface):
    """Describes a model as generated by this library
    """
    
    schema = zope.schema.InterfaceField(title=u"Default schema",
                                        readonly=True)
    
    metadata = zope.schema.Dict(title=u"Default schema metadata",
                                description=u"Metadata is managed by third party utilities",
                                key_type=zope.schema.TextLine(title=u"Arbitrary key"),
                                value_type=zope.schema.Object(title=u"Arbitrary value",
                                                              schema=Interface),
                                readonly=True)
    
    schemata = zope.schema.Dict(title=u"Schemata",
                                key_type=zope.schema.TextLine(title=u"Schema name",
                                        description=u"Default schema is under the key u''."),
                                value_type=zope.schema.Object(title=u"Schema interface",
                                        description=u"Metadata dict is a tagged value under the key 'plone.supermodel.metadata'",
                                        schema=IInterface))
    
    def lookup_schema(schema=u""):
        """Return the schema with the given name, or None if it cannot be 
        found.
        """
    
    def lookup_metadata(self, schema=u""):
        """Return the metadata dict for the schema with the given name.
        Returns None if the schema cannot be found.
        """

class IXMLToSchema(Interface):
    """Functionality to parse an XML representation of a schema and return
    an interface representation with zope.schema fields.
    
    A file can be parsed purely for a schema. This allows syntax like:
    
        class IMyType( xml_schema('schema.xml') ):
            pass
        
    To get more detailed information, including metadata that is read and
    populated by third party plugins, use:
    
        model = load_file('schema.xml')
    """
    
    def xml_schema(filename, schema=u"", policy=u""):
        """Given a filename relative to the current module, return an
        interface representing the schema contained in that file. If there
        are multiple <schema /> blocks, return the unnamed one, unless 
        a name is supplied, in which case the 'name' attribute of the schema
        will be matched to the schema name.
        
        The policy argument can be used to pick a different parsing policy.
        Policies must be registered as named utilities providing
        ISchemaPolicy.
        
        Raises a KeyError if the schema cannot be found.
        Raises an IOError if the file cannot be opened.
        """
    
    def load_file(filename, reload=False, policy=u""):
        """Return an IModel as contained in the given XML file, which is read
        relative to the current module (unless it is an absolute path).
        
        If reload is True, reload a schema even if it's cached. If policy
        is given, it can be used to select a custom schema parsing policy.
        Policies must be registered as named utilities providing
        ISchemaPolicy.
        """
    
    def load_string(model, policy=u""):
        """Load a model from a string rather than a file.
        """
    
    def serialize_schema(schema, name=u""):
        """Return an XML string representing the given schema interface. This
        is a convenience method around the serialize_model() method, below.
        """
    def serialize_model(model):
        """Return an XML string representing the given model, as returned by
        the load_file() or load_string() method.
        """

class ISchemaPolicy(Interface):
    """A utility that provides some basic attributes of the generated
    schemata. Provide a custom one to make policy decisions about where
    generated schemata live, what bases they have and how they are named.
    """

    def module(schema_name, tree):
        """Return the module name to use.
        """
        
    def bases(schema_name, tree):
        """Return the bases to use.
        """
        
    def name(schema_name, tree):
        """Return the schema name to use
        """
        
class IFieldExportImportHandler(Interface):
    """Named utilities corresponding to node names should be registered for
    this interface. They will be called upon to build a schema fields out of
    DOM ndoes.
    """
    
    def read(node):
        """Read a field from the node and return a new instance
        """
        
    def write(field, field_name, field_type):
        """Create and return a new node representing the given field
        """
        
class ISchemaMetadataHandler(Interface):
    """A third party application can register named utilities providing this
    interface. For each schema that is parsed in a model, the read() method
    will be called.
    """
    
    namespace = zope.schema.URI(title=u"XML namespace used by this handler", required=False)
    prefix = zope.schema.ASCII(title=u"Preferred XML schema namespace for serialisation", required=False)
    
    def read(schema_node, schema, schema_metadata):
        """Called once the schema in the given <schema /> node has been
        read. schema is the schema interface that was read. schema_metadata 
        is a dict that can be written to, containing the current set of 
        metadata for this schema, specific to this handler.
        """

    def write(schema_node, schema, schema_metadata):
        """Write the metadata contained in the schema_metadata, which pertains
        to the given schema, to the schema_node. The node will already exist
        and be populated with standard data.
        """

class IFieldMetadataHandler(Interface):
    """A third party application can register named utilities providing this
    interface. For each field that is parsed in a schema, the read() method
    will be called.
    """
    
    namespace = zope.schema.URI(title=u"XML namespace used by this handler", required=False)
    prefix = zope.schema.ASCII(title=u"Preferred XML schema namespace for serialisation", required=False)
    
    def read(field_node, field, schema_metadata):
        """Called once the field in the given <field /> node has been
        read. field is the field instance that was read. schema_metadata 
        is a dict that can be written to, containing the current set of 
        metadata for this schema, specific to this handler.
        """
    
    def write(field_node, field, schema_metadata):
        """Write the metadata contained in the schema_metadata, which pertains
        to the given field, to the field_node. The node will already exist
        and be populated with standard data.
        """