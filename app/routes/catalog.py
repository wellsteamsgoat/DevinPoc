"""Catalog browsing endpoints for Dremio instances."""

import logging

from flask_restx import Namespace, Resource

from app.dremio_client import DremioClient
from app.models.schemas import catalog_request_model

logger = logging.getLogger(__name__)

catalog_ns = Namespace("catalog", description="Browse Dremio catalog")

# Re-register the model in this namespace so Swagger picks it up
catalog_ns.models[catalog_request_model.name] = catalog_request_model
for dep in catalog_request_model.__schema__:
    pass  # ensure nested models are loaded


def _build_client(data):
    return DremioClient(
        base_url=data["dremio_url"],
        pat=data.get("pat") or None,
        username=data.get("username") or None,
        password=data.get("password") or None,
    )


@catalog_ns.route("/browse")
class CatalogBrowse(Resource):
    """Browse the Dremio catalog."""

    @catalog_ns.expect(catalog_request_model, validate=True)
    @catalog_ns.doc(description="Browse the Dremio catalog at the given path.")
    def post(self):
        """Browse catalog entities.

        Provide connection details and an optional path. Returns the list
        of entities at that location.
        """
        data = catalog_ns.payload
        try:
            client = _build_client(data)
            path = data.get("path")
            if path:
                entity = client.get_catalog_entity_by_path(path)
                children = entity.get("children", [])
                return {
                    "entity": {
                        "id": entity.get("id"),
                        "path": entity.get("path"),
                        "type": entity.get("entityType"),
                    },
                    "children": children,
                }
            else:
                catalog = client.get_catalog()
                return {"entities": catalog.get("data", [])}
        except Exception as exc:
            logger.exception("Error browsing catalog")
            catalog_ns.abort(500, str(exc))
