"""Swagger models for the Dremio Cloner API."""

from flask_restx import Namespace, fields

# -------------------------------------------------------------------
# Shared model definitions used across multiple namespaces
# -------------------------------------------------------------------

_ns = Namespace("models", description="Shared Swagger models")

connection_model = _ns.model(
    "DremioConnection",
    {
        "dremio_url": fields.String(
            required=True,
            description="Base URL of the Dremio instance (e.g. http://localhost:9047)",
            example="http://localhost:9047",
        ),
        "pat": fields.String(
            required=False,
            description="Personal Access Token (use this OR username/password)",
            example="",
        ),
        "username": fields.String(
            required=False,
            description="Username (used when PAT is not provided)",
            example="admin",
        ),
        "password": fields.String(
            required=False,
            description="Password (used when PAT is not provided)",
            example="",
        ),
    },
)

clone_request_model = _ns.model(
    "CloneRequest",
    {
        "source": fields.Nested(
            connection_model,
            required=True,
            description="Source Dremio connection details",
        ),
        "target": fields.Nested(
            connection_model,
            required=True,
            description="Target Dremio connection details",
        ),
    },
)

clone_spaces_request_model = _ns.model(
    "CloneSpacesRequest",
    {
        "source": fields.Nested(connection_model, required=True),
        "target": fields.Nested(connection_model, required=True),
        "space_names": fields.List(
            fields.String,
            required=False,
            description="Specific space names to clone. If empty, all spaces are cloned.",
            example=["space1", "space2"],
        ),
    },
)

clone_vds_request_model = _ns.model(
    "CloneVDSRequest",
    {
        "source": fields.Nested(connection_model, required=True),
        "target": fields.Nested(connection_model, required=True),
        "space_names": fields.List(
            fields.String,
            required=False,
            description="Limit VDS cloning to specific spaces. If empty, all spaces are processed.",
            example=[],
        ),
    },
)

clone_reflections_request_model = _ns.model(
    "CloneReflectionsRequest",
    {
        "source": fields.Nested(connection_model, required=True),
        "target": fields.Nested(connection_model, required=True),
        "dataset_paths": fields.List(
            fields.List(fields.String),
            required=False,
            description=(
                "Specific dataset paths whose reflections should be cloned. "
                'Each path is a list of path components, e.g. [["space1","vds1"]]. '
                "If empty, reflections for all datasets are cloned."
            ),
            example=[["space1", "my_view"]],
        ),
    },
)

clone_wikis_tags_request_model = _ns.model(
    "CloneWikisTagsRequest",
    {
        "source": fields.Nested(connection_model, required=True),
        "target": fields.Nested(connection_model, required=True),
        "entity_paths": fields.List(
            fields.List(fields.String),
            required=False,
            description=(
                "Specific entity paths whose wikis/tags should be cloned. "
                "If empty, all entities are processed."
            ),
            example=[["space1"]],
        ),
    },
)

catalog_request_model = _ns.model(
    "CatalogRequest",
    {
        "dremio_url": fields.String(
            required=True,
            description="Base URL of the Dremio instance",
            example="http://localhost:9047",
        ),
        "pat": fields.String(required=False, description="Personal Access Token"),
        "username": fields.String(required=False, description="Username"),
        "password": fields.String(required=False, description="Password"),
        "path": fields.List(
            fields.String,
            required=False,
            description="Path components to browse. If empty, lists top-level entities.",
            example=[],
        ),
    },
)
