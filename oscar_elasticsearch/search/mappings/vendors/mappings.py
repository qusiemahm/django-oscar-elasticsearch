# search/mappings/vendors/mappings.py

import odin
from oscar.core.loading import get_class

OscarBaseMapping = get_class("oscar_odin.mappings.common", "OscarBaseMapping")
VendorResource = get_class("oscar_odin.resources.vendor", "VendorResource")

from .resources import VendorElasticSearchResource

class VendorMapping(OscarBaseMapping):
    """
    Mapping class to transform data from VendorResource to VendorElasticSearchResource 
    before sending it to Elasticsearch.
    """
    from_resource = VendorResource
    to_resource = VendorElasticSearchResource

    register_mapping = False  # Set to True if you want it auto-registered

    # Example direct field copies (where from_field and to_field match).
    mappings = (
        odin.define(from_field="id", to_field="id"),
        odin.define(from_field="user_id", to_field="user_id"),
        odin.define(from_field="registration_date", to_field="registration_date"),
        odin.define(from_field="registration_status", to_field="registration_status"),
        odin.define(from_field="rating", to_field="rating"),
        odin.define(from_field="total_ratings", to_field="total_ratings"),
        odin.define(from_field="is_valid", to_field="is_valid"),
    )

    @odin.map_field(from_field="company_name", to_field="name")
    def map_company_name(self, company_name: str):
        return company_name

    @odin.map_field(from_field="brand_name", to_field="brand_name")
    def map_brand_name(self, brand_name: str):
        return brand_name

    @odin.map_field(from_field="brand_name_en", to_field="brand_name_en")
    def map_brand_name_en(self, brand_name_en: str):
        return brand_name_en
    
    @odin.map_field(from_field="brand_name_ar", to_field="brand_name_ar")
    def map_brand_name_ar(self, brand_name_ar: str):
        return brand_name_ar
    # @odin.assign_field(to_list=True)
    # def status(self):
    #     """
    #     Example: Some logic to put 'approved' or 'rejected' in a list for filtering.
    #     If your vendor is private or restricted, you could reflect that here.
    #     """
    #     statuses = []
    #     if self.source.registration_status == "approved":
    #         statuses.append("approved")
    #     else:
    #         statuses.append("unapproved")
    #     return statuses

    @odin.assign_field
    def content_type(self):
        """
        A field to identify this doc type, if needed.
        """
        return "vendor"

    @odin.map_field(from_field="brand_name", to_field="search_title")
    def map_search_title(self, brand_name: str):
        return brand_name