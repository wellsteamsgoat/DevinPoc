"""Clone endpoints for copying Dremio resources between instances."""

import logging

from flask_restx import Namespace, Resource

from app.dremio_client import DremioClient
from app.models.schemas import (
    clone_reflections_request_model,
    clone_request_model,
    clone_spaces_request_model,
    clone_vds_request_model,
    clone_wikis_tags_request_model,
)

logger = logging.getLogger(__name__)

clone_ns = Namespace("clone", description="Clone Dremio resources")

# Register shared models into this namespace
for model in (
    clone_request_model,
    clone_spaces_request_model,
    clone_vds_request_model,
    clone_reflections_request_model,
    clone_wikis_tags_request_model,
):
    clone_ns.models[model.name] = model


def _build_clients(data):
    """Return (source_client, target_client) from the request payload."""
    src = data["source"]
    tgt = data["target"]
    source_client = DremioClient(
        base_url=src["dremio_url"],
        pat=src.get("pat") or None,
        username=src.get("username") or None,
        password=src.get("password") or None,
    )
    target_client = DremioClient(
        base_url=tgt["dremio_url"],
        pat=tgt.get("pat") or None,
        username=tgt.get("username") or None,
        password=tgt.get("password") or None,
    )
    return source_client, target_client


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------


def _clone_spaces(source_client, target_client, space_names=None):
    """Clone spaces from source to target.

    Returns a report dict with cloned / skipped / failed counts.
    """
    catalog = source_client.get_catalog()
    spaces = [
        e for e in catalog.get("data", [])
        if e.get("containerType") == "SPACE"
    ]

    if space_names:
        name_set = set(space_names)
        spaces = [s for s in spaces if s.get("path", [None])[0] in name_set]

    cloned, skipped, errors = [], [], []
    for space in spaces:
        name = space.get("path", [None])[0]
        try:
            target_client.get_catalog_entity_by_path([name])
            skipped.append(name)
            logger.info("Space '%s' already exists in target – skipped", name)
        except Exception:
            try:
                target_client.create_catalog_entity(
                    {"entityType": "space", "name": name}
                )
                cloned.append(name)
                logger.info("Cloned space '%s'", name)
            except Exception as exc:
                errors.append({"space": name, "error": str(exc)})
                logger.exception("Failed to clone space '%s'", name)

    return {"cloned": cloned, "skipped": skipped, "errors": errors}


def _collect_children(client, entity_id, collected=None):
    """Recursively collect all children of an entity."""
    if collected is None:
        collected = []
    entity = client.get_catalog_entity_by_id(entity_id)
    for child in entity.get("children", []):
        child_detail = client.get_catalog_entity_by_id(child["id"])
        collected.append(child_detail)
        container = child_detail.get("entityType") in ("folder",)
        if container:
            _collect_children(client, child["id"], collected)
    return collected


def _clone_folders(source_client, target_client, space_name):
    """Clone the folder tree of a given space from source to target."""
    cloned, skipped, errors = [], [], []
    try:
        source_space = source_client.get_catalog_entity_by_path([space_name])
    except Exception:
        return {"cloned": cloned, "skipped": skipped, "errors": errors}

    all_children = _collect_children(source_client, source_space["id"])
    folders = [c for c in all_children if c.get("entityType") == "folder"]

    for folder in folders:
        folder_path = folder.get("path", [])
        try:
            target_client.get_catalog_entity_by_path(folder_path)
            skipped.append(folder_path)
        except Exception:
            try:
                parent_path = folder_path[:-1]
                parent = target_client.get_catalog_entity_by_path(parent_path)
                target_client.create_catalog_entity(
                    {
                        "entityType": "folder",
                        "path": folder_path,
                    }
                )
                cloned.append(folder_path)
            except Exception as exc:
                errors.append({"folder": folder_path, "error": str(exc)})

    return {"cloned": cloned, "skipped": skipped, "errors": errors}


def _clone_vds_for_space(source_client, target_client, space_name):
    """Clone all VDS (virtual datasets) within a space."""
    cloned, skipped, errors = [], [], []
    try:
        source_space = source_client.get_catalog_entity_by_path([space_name])
    except Exception:
        return {"cloned": cloned, "skipped": skipped, "errors": errors}

    all_children = _collect_children(source_client, source_space["id"])
    datasets = [
        c for c in all_children
        if c.get("type") == "VIRTUAL_DATASET"
        or c.get("entityType") == "dataset"
        and c.get("type") == "VIRTUAL_DATASET"
    ]

    for ds in datasets:
        ds_path = ds.get("path", [])
        try:
            target_client.get_catalog_entity_by_path(ds_path)
            skipped.append(ds_path)
        except Exception:
            try:
                sql = ds.get("sql", "")
                sql_context = ds.get("sqlContext", [])
                target_client.create_catalog_entity(
                    {
                        "entityType": "dataset",
                        "type": "VIRTUAL_DATASET",
                        "path": ds_path,
                        "sql": sql,
                        "sqlContext": sql_context,
                    }
                )
                cloned.append(ds_path)
            except Exception as exc:
                errors.append({"dataset": ds_path, "error": str(exc)})

    return {"cloned": cloned, "skipped": skipped, "errors": errors}


def _clone_reflections_for_dataset(source_client, target_client, dataset_path):
    """Clone reflections from one dataset to the corresponding target dataset."""
    cloned, errors = [], []
    try:
        src_ds = source_client.get_catalog_entity_by_path(dataset_path)
        tgt_ds = target_client.get_catalog_entity_by_path(dataset_path)
    except Exception as exc:
        return {"cloned": cloned, "errors": [{"path": dataset_path, "error": str(exc)}]}

    try:
        reflections = source_client.get_reflections(src_ds["id"])
    except Exception:
        reflections = {"data": []}

    for ref in reflections.get("data", []):
        try:
            ref_payload = {
                "type": ref.get("type"),
                "name": ref.get("name"),
                "datasetId": tgt_ds["id"],
                "enabled": ref.get("enabled", True),
                "displayFields": ref.get("displayFields", []),
                "dimensionFields": ref.get("dimensionFields", []),
                "measureFields": ref.get("measureFields", []),
                "sortFields": ref.get("sortFields", []),
                "partitionFields": ref.get("partitionFields", []),
                "distributionFields": ref.get("distributionFields", []),
            }
            target_client.create_reflection(ref_payload)
            cloned.append(ref.get("name"))
        except Exception as exc:
            errors.append({"reflection": ref.get("name"), "error": str(exc)})

    return {"cloned": cloned, "errors": errors}


def _clone_wiki_and_tags(source_client, target_client, entity_path):
    """Clone wiki and tags for a single entity."""
    results = {"wiki": None, "tags": None, "errors": []}
    try:
        src_entity = source_client.get_catalog_entity_by_path(entity_path)
        tgt_entity = target_client.get_catalog_entity_by_path(entity_path)
    except Exception as exc:
        results["errors"].append(str(exc))
        return results

    # Wiki
    wiki = source_client.get_wiki(src_entity["id"])
    if wiki:
        try:
            target_client.set_wiki(
                tgt_entity["id"], {"text": wiki.get("text", "")}
            )
            results["wiki"] = "cloned"
        except Exception as exc:
            results["errors"].append(f"wiki: {exc}")

    # Tags
    tags = source_client.get_tags(src_entity["id"])
    if tags:
        try:
            target_client.set_tags(
                tgt_entity["id"], {"tags": tags.get("tags", [])}
            )
            results["tags"] = "cloned"
        except Exception as exc:
            results["errors"].append(f"tags: {exc}")

    return results


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@clone_ns.route("/spaces")
class CloneSpaces(Resource):
    """Clone spaces from source to target Dremio."""

    @clone_ns.expect(clone_spaces_request_model, validate=True)
    @clone_ns.doc(description="Clone spaces (and their folder structures) from source to target.")
    def post(self):
        """Clone spaces.

        Creates spaces that exist in the source but not in the target.
        Optionally filter by space names.
        """
        data = clone_ns.payload
        try:
            source_client, target_client = _build_clients(data)
            space_names = data.get("space_names")
            report = _clone_spaces(source_client, target_client, space_names)

            # Also clone folder structure for each successfully cloned space
            folder_reports = {}
            for name in report["cloned"] + report["skipped"]:
                folder_reports[name] = _clone_folders(
                    source_client, target_client, name
                )

            return {
                "spaces": report,
                "folders": folder_reports,
            }
        except Exception as exc:
            logger.exception("Error cloning spaces")
            clone_ns.abort(500, str(exc))


@clone_ns.route("/vds")
class CloneVDS(Resource):
    """Clone virtual datasets from source to target Dremio."""

    @clone_ns.expect(clone_vds_request_model, validate=True)
    @clone_ns.doc(description="Clone virtual datasets (VDS/views) from source to target.")
    def post(self):
        """Clone virtual datasets.

        Iterates over spaces in the source, discovers all VDS, and recreates
        them in the target.
        """
        data = clone_ns.payload
        try:
            source_client, target_client = _build_clients(data)
            space_filter = data.get("space_names")

            catalog = source_client.get_catalog()
            spaces = [
                e for e in catalog.get("data", [])
                if e.get("containerType") == "SPACE"
            ]
            if space_filter:
                name_set = set(space_filter)
                spaces = [
                    s for s in spaces if s.get("path", [None])[0] in name_set
                ]

            results = {}
            for space in spaces:
                name = space.get("path", [None])[0]
                results[name] = _clone_vds_for_space(
                    source_client, target_client, name
                )

            return {"vds": results}
        except Exception as exc:
            logger.exception("Error cloning VDS")
            clone_ns.abort(500, str(exc))


@clone_ns.route("/reflections")
class CloneReflections(Resource):
    """Clone reflections from source to target Dremio."""

    @clone_ns.expect(clone_reflections_request_model, validate=True)
    @clone_ns.doc(description="Clone reflections from source datasets to target datasets.")
    def post(self):
        """Clone reflections.

        If dataset_paths is provided, only those datasets are processed.
        Otherwise all datasets in all spaces are scanned.
        """
        data = clone_ns.payload
        try:
            source_client, target_client = _build_clients(data)
            dataset_paths = data.get("dataset_paths")

            if dataset_paths:
                results = {}
                for dp in dataset_paths:
                    key = ".".join(dp)
                    results[key] = _clone_reflections_for_dataset(
                        source_client, target_client, dp
                    )
                return {"reflections": results}

            # Discover all datasets across all spaces
            catalog = source_client.get_catalog()
            spaces = [
                e for e in catalog.get("data", [])
                if e.get("containerType") == "SPACE"
            ]
            results = {}
            for space in spaces:
                space_detail = source_client.get_catalog_entity_by_id(
                    space["id"]
                )
                all_children = _collect_children(
                    source_client, space_detail["id"]
                )
                datasets = [
                    c for c in all_children
                    if c.get("type") == "VIRTUAL_DATASET"
                ]
                for ds in datasets:
                    dp = ds.get("path", [])
                    key = ".".join(dp)
                    results[key] = _clone_reflections_for_dataset(
                        source_client, target_client, dp
                    )
            return {"reflections": results}
        except Exception as exc:
            logger.exception("Error cloning reflections")
            clone_ns.abort(500, str(exc))


@clone_ns.route("/wikis-tags")
class CloneWikisTags(Resource):
    """Clone wikis and tags from source to target Dremio."""

    @clone_ns.expect(clone_wikis_tags_request_model, validate=True)
    @clone_ns.doc(description="Clone wiki content and tags from source to target.")
    def post(self):
        """Clone wikis and tags.

        Copies wiki text and tags for specified entities, or for all
        top-level entities if none are specified.
        """
        data = clone_ns.payload
        try:
            source_client, target_client = _build_clients(data)
            entity_paths = data.get("entity_paths")

            if entity_paths:
                results = {}
                for ep in entity_paths:
                    key = ".".join(ep)
                    results[key] = _clone_wiki_and_tags(
                        source_client, target_client, ep
                    )
                return {"wikis_tags": results}

            # Process all top-level entities
            catalog = source_client.get_catalog()
            results = {}
            for entity in catalog.get("data", []):
                path = entity.get("path", [])
                key = ".".join(path)
                results[key] = _clone_wiki_and_tags(
                    source_client, target_client, path
                )
            return {"wikis_tags": results}
        except Exception as exc:
            logger.exception("Error cloning wikis/tags")
            clone_ns.abort(500, str(exc))


@clone_ns.route("/all")
class CloneAll(Resource):
    """Clone all resources from source to target Dremio."""

    @clone_ns.expect(clone_request_model, validate=True)
    @clone_ns.doc(
        description=(
            "Clone everything: spaces, folders, VDS, reflections, wikis, "
            "and tags from source to target."
        )
    )
    def post(self):
        """Clone all resources.

        Performs a full clone: spaces -> folders -> VDS -> reflections
        -> wikis & tags.
        """
        data = clone_ns.payload
        try:
            source_client, target_client = _build_clients(data)
            report = {}

            # 1. Spaces
            space_report = _clone_spaces(source_client, target_client)
            report["spaces"] = space_report

            # 2. Folders for each space
            catalog = source_client.get_catalog()
            spaces = [
                e for e in catalog.get("data", [])
                if e.get("containerType") == "SPACE"
            ]
            folder_report = {}
            for space in spaces:
                name = space.get("path", [None])[0]
                folder_report[name] = _clone_folders(
                    source_client, target_client, name
                )
            report["folders"] = folder_report

            # 3. VDS
            vds_report = {}
            for space in spaces:
                name = space.get("path", [None])[0]
                vds_report[name] = _clone_vds_for_space(
                    source_client, target_client, name
                )
            report["vds"] = vds_report

            # 4. Reflections for all datasets
            reflection_report = {}
            for space in spaces:
                space_detail = source_client.get_catalog_entity_by_id(
                    space["id"]
                )
                all_children = _collect_children(
                    source_client, space_detail["id"]
                )
                datasets = [
                    c for c in all_children
                    if c.get("type") == "VIRTUAL_DATASET"
                ]
                for ds in datasets:
                    dp = ds.get("path", [])
                    key = ".".join(dp)
                    reflection_report[key] = _clone_reflections_for_dataset(
                        source_client, target_client, dp
                    )
            report["reflections"] = reflection_report

            # 5. Wikis & tags for all top-level entities
            wikis_tags_report = {}
            for entity in catalog.get("data", []):
                path = entity.get("path", [])
                key = ".".join(path)
                wikis_tags_report[key] = _clone_wiki_and_tags(
                    source_client, target_client, path
                )
            report["wikis_tags"] = wikis_tags_report

            return report
        except Exception as exc:
            logger.exception("Error during full clone")
            clone_ns.abort(500, str(exc))
