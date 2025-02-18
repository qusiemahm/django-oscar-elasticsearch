# search/mappings/vendors/documents.py

import odin
from oscar.core.loading import get_class

OscarResource = get_class("oscar_odin.resources.base", "OscarResource")
VendorElasticSearchResource = get_class("search.mappings.vendors.resources", "VendorElasticSearchResource")
VendorMapping = get_class("search.mappings.vendors.mappings", "VendorMapping")
VendorResource = get_class("oscar_odin.resources.vendor", "VendorResource")

OscarBaseMapping = get_class("oscar_odin.mappings.common", "OscarBaseMapping")

class VendorElasticSearchDocument(OscarResource):
    _index: str
    _id: str
    _source: VendorElasticSearchResource
    _op_type: str = "index"
    

class VendorElasticSearchMapping(OscarBaseMapping):
    """
    Final step that merges the _index, _id, and the mapped resource for ES.
    """
    from_resource = VendorResource
    to_resource = VendorElasticSearchDocument

    register_mapping = False

    # A single field mapping for _id from vendor.id
    mappings = (
        odin.define(from_field="id", to_field="_id"),
    )

    @odin.assign_field
    def _index(self) -> str:
        """
        Provide the name of the index. 
        Could dynamically come from self.context or your settings.
        """
        return self.context.get("_index", "vendors")

    @odin.assign_field
    def _source(self):
        """
        Actually apply the vendor mapping => VendorElasticSearchResource
        """
        return VendorMapping.apply(self.source, self.context)
