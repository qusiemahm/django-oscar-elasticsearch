# search/mappings/vendors/resources.py

from oscar_odin.fields import DecimalField
from odin.fields import StringField, DateTimeField, BooleanField, IntegerField
from oscar_elasticsearch.search.mappings.mixins import OscarElasticSearchResourceMixin
from oscar.core.loading import get_class
from datetime import datetime
from odin import fields

OscarResource = get_class("oscar_odin.resources.base", "OscarResource")

class VendorElasticSearchResource(OscarElasticSearchResourceMixin):
    """
    A resource describing the structure we want to store for a Vendor in Elasticsearch.
    We extend OscarElasticSearchResourceMixin for convenience, 
    which provides some common fields and behaviors for indexing.
    """
    id: int = IntegerField()
    user_id: int = IntegerField()
    name: str = StringField()
    brand_name: str = StringField()
    brand_name_en: str = StringField()
    brand_name_ar: str = StringField()
    search_title: str = StringField(null=True)
    rating: float = DecimalField()
    total_ratings: int = IntegerField()      
    registration_date: datetime = DateTimeField()
    registration_status: str = StringField()
    is_valid: bool = BooleanField()
    brand_name_en_autocomplete = fields.StringField(null=True)
    brand_name_ar_autocomplete = fields.StringField(null=True)
    suggest = fields.DictField(null=True)           # e.g. from business_details

    # status = fields.ListField(of=fields.StringField(), null=True)