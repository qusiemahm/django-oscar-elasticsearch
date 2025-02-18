# # search/mappings/vendors/vendor_resource.py

# import odin
# from django.utils.functional import cached_property
# from oscar.core.loading import get_model, get_class

# Vendor = get_model("vendor", "Vendor")

# class VendorResource(odin.Resource):
#     """
#     Maps your Django Vendor model instance into a data structure 
#     that Odin can pass to the ES resource (VendorElasticSearchResource).
#     """
#     id = odin.Integer()
#     user_id = odin.Integer()
#     registration_date = odin.DateTime()
#     registration_status = odin.String()
#     rating = odin.Float()
#     total_ratings = odin.Integer()
#     # We'll store "company_name" from the Vendor's legal_information
#     # and "brand_name" from business_details, etc.
#     company_name = odin.String(nullable=True)
#     brand_name = odin.String(nullable=True)
#     is_valid = odin.Boolean()

#     class Meta:
#         name = "VendorResource"

#     @classmethod
#     def from_model_instance(cls, instance: Vendor, *args, **kwargs):
#         """
#         Build the resource from the actual Vendor model instance.
#         """
#         legal_info = getattr(instance, "legal_information", None)
#         business_details = getattr(instance, "business_details", None)

#         return cls(
#             id=instance.id,
#             user_id=instance.user_id,
#             registration_date=instance.registration_date,
#             registration_status=instance.registration_status,
#             rating=instance.rating,
#             total_ratings=instance.total_ratings,
#             company_name=(
#                 legal_info.company_name if legal_info and legal_info.company_name else "Unknown"
#             ),
#             brand_name=(
#                 business_details.brand_name if business_details and business_details.brand_name else ""
#             ),
#             is_valid=instance.is_valid,
#         )
