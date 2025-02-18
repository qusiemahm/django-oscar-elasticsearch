from elasticsearch import Elasticsearch
from odin.codecs import dict_codec
from django.db.models import QuerySet
from oscar.core.loading import get_class, get_model, get_classes
from oscar_elasticsearch.search import settings

# Get index settings for vendors
(
    OSCAR_VENDORS_INDEX_NAME,
    OSCAR_VENDOR_SEARCH_FIELDS,
    get_vendors_index_mapping,
    get_oscar_index_settings,
) = get_classes(
    "search.indexing.settings",
    [
        "OSCAR_VENDORS_INDEX_NAME",
        "OSCAR_VENDOR_SEARCH_FIELDS",
        "get_vendors_index_mapping",
        "get_oscar_index_settings",
    ],
)

BaseElasticSearchApi = get_class("search.api.search", "BaseElasticSearchApi")
ESModelIndexer = get_class("search.indexing.indexer", "ESModelIndexer")
Vendor = get_model("vendor", "Vendor")


class VendorElasticsearchIndex(BaseElasticSearchApi, ESModelIndexer):
    """
    Elasticsearch indexer for Vendors (similar to ProductElasticsearchIndex).
    """

    Model = Vendor
    INDEX_NAME = OSCAR_VENDORS_INDEX_NAME
    INDEX_MAPPING = get_vendors_index_mapping()
    INDEX_SETTINGS = get_oscar_index_settings()
    SEARCH_FIELDS = OSCAR_VENDOR_SEARCH_FIELDS
    SUGGESTION_FIELD_NAME = settings.SUGGESTION_FIELD_NAME
    context = {}

    def get_filters(self, filters):
        """
        Define filters for searching vendors (e.g., only active ones).
        """
        if filters is not None:
            return filters

        return [{"term": {"registration_status": "approved"}}]  # Only approved vendors

    def create_index_if_missing(self):
        """
        Check if the Elasticsearch index exists, and create it if it does not.
        """
        from django.conf import settings

        es = Elasticsearch(settings.ELASTICSEARCH_DSL['default']['hosts'])

        alias_name = self.INDEX_NAME  # Alias for searching
        new_index_name = f"{alias_name}_001"  # Versioned index name

        # Check if alias exists
        alias_exists = es.indices.exists_alias(name=alias_name)

        if alias_exists:
            print(f"✅ Alias '{alias_name}' already exists. No need to create an index.")
            return

        print(f"🔍 Alias '{alias_name}' not found. Checking index...")

        # Check if the versioned index exists
        if not es.indices.exists(index=new_index_name):
            print(f"🔍 Index '{new_index_name}' not found. Creating it...")

            es.indices.create(
                index=new_index_name,
                body={
                    "settings": self.INDEX_SETTINGS,
                    "mappings": self.INDEX_MAPPING,
                },
            )
            print(f"✅ Index '{new_index_name}' created successfully.")

        # Ensure alias points to the new index
        es.indices.update_aliases(body={
            "actions": [
                {"add": {"index": new_index_name, "alias": alias_name}}
            ]
        })
        print(f"✅ Alias '{alias_name}' now points to '{new_index_name}'.")


    def update_or_create(self, objects):
        """
        Override `update_or_create` to ensure the index exists before indexing vendors.
        """
        self.create_index_if_missing()
        super().update_or_create(objects)

    def make_documents(self, objects):
        """
        Convert Vendor queryset into Elasticsearch documents.
        """
        if not isinstance(objects, QuerySet):
            try:
                objects = Vendor.objects.filter(id__in=[o.id for o in objects])
            except:
                raise ValueError(
                    "Argument 'objects' must be a QuerySet, as vendor_queryset_to_resources requires a QuerySet, got %s"
                    % type(objects)
                )

        vendor_queryset_to_resources = get_class(
            "oscar_odin.mappings.vendors", "vendor_queryset_to_resources"
        )

        VendorElasticSearchMapping = get_class(
            "search.mappings.vendors", "VendorElasticSearchMapping"
        )

        # Convert Django Vendor queryset into Odin resources
        vendor_resources = vendor_queryset_to_resources(objects)

        # Apply VendorElasticSearchMapping
        vendor_document_resources = VendorElasticSearchMapping.apply(
            vendor_resources, self.context
        )

        # ✅ Populate autocomplete fields
        for doc in vendor_document_resources:
            doc._source.brand_name_en_autocomplete = doc._source.brand_name_en or ""
            doc._source.brand_name_ar_autocomplete = doc._source.brand_name_ar or ""
            doc._source.suggest = {
                "input": [doc._source.brand_name_en, doc._source.brand_name_ar],
                "weight": 10,
                "contexts": {"status": ["approved" if doc._source.is_valid else "pending"]}
            }


        # Convert to Elasticsearch document format
        return dict_codec.dump(vendor_document_resources, include_type_field=False)

    def autocomplete_search(self, query_string, from_=0, to=10):
        """
        Autocomplete search for vendors using edge_ngram_analyzer.
        """
        # Use a "multi_match" query to search across autocomplete fields
        search_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query_string,
                            "fields": [
                                "brand_name_en.autocomplete^3",
                                "brand_name_ar.autocomplete^3",
                                "name.autocomplete^2",
                            ],
                            "type": "phrase_prefix"  # Match prefixes of terms
                        }
                    }
                ],
                "filter": [
                    {"term": {"is_valid": True}}  # Optional: Filter valid vendors
                ]
            }
        }

        search_response = self.search(
            from_=from_,
            to=to,
            query_string=None,
            search_fields=[],
            filters=[search_query]
        )

        return search_response


