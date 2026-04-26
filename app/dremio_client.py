"""Dremio REST API client for interacting with Dremio instances."""

import logging
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


class DremioClient:
    """Client for the Dremio REST API (v3)."""

    def __init__(self, base_url, pat=None, username=None, password=None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        if pat:
            self.session.headers.update({"Authorization": f"Bearer {pat}"})
        elif username and password:
            token = self._login(username, password)
            self.session.headers.update({"Authorization": f"_dremio{token}"})
        else:
            raise ValueError(
                "Either a PAT or username/password must be provided."
            )

    def _login(self, username, password):
        """Authenticate with username/password and return a session token."""
        url = f"{self.base_url}/apiv2/login"
        payload = {"userName": username, "password": password}
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["token"]

    # ------------------------------------------------------------------
    # Catalog operations
    # ------------------------------------------------------------------

    def get_catalog(self):
        """List all top-level catalog entities."""
        url = f"{self.base_url}/api/v3/catalog"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_catalog_entity_by_id(self, entity_id):
        """Get a catalog entity by its ID."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_catalog_entity_by_path(self, path_parts):
        """Get a catalog entity by its path.

        Args:
            path_parts: list of path components, e.g. ["space1", "folder1"]
        """
        encoded = "/".join(quote(p, safe="") for p in path_parts)
        url = f"{self.base_url}/api/v3/catalog/by-path/{encoded}"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def create_catalog_entity(self, entity_payload):
        """Create a new catalog entity (space, source, folder, dataset)."""
        url = f"{self.base_url}/api/v3/catalog"
        resp = self.session.post(url, json=entity_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def update_catalog_entity(self, entity_id, entity_payload):
        """Update an existing catalog entity."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}"
        resp = self.session.put(url, json=entity_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def delete_catalog_entity(self, entity_id, tag=None):
        """Delete a catalog entity by its ID."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}"
        params = {}
        if tag:
            params["tag"] = tag
        resp = self.session.delete(url, params=params, timeout=30)
        resp.raise_for_status()

    # ------------------------------------------------------------------
    # Reflection operations
    # ------------------------------------------------------------------

    def get_reflections(self, dataset_id):
        """Get reflections for a dataset."""
        url = f"{self.base_url}/api/v3/dataset/{dataset_id}/reflection"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_reflection_by_id(self, reflection_id):
        """Get a specific reflection by ID."""
        url = f"{self.base_url}/api/v3/reflection/{reflection_id}"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def create_reflection(self, reflection_payload):
        """Create a new reflection."""
        url = f"{self.base_url}/api/v3/reflection"
        resp = self.session.post(url, json=reflection_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Wiki operations
    # ------------------------------------------------------------------

    def get_wiki(self, entity_id):
        """Get the wiki for a catalog entity."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}/collaboration/wiki"
        resp = self.session.get(url, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def set_wiki(self, entity_id, wiki_payload):
        """Set the wiki for a catalog entity."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}/collaboration/wiki"
        resp = self.session.post(url, json=wiki_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Tag operations
    # ------------------------------------------------------------------

    def get_tags(self, entity_id):
        """Get the tags for a catalog entity."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}/collaboration/tag"
        resp = self.session.get(url, timeout=30)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def set_tags(self, entity_id, tags_payload):
        """Set the tags for a catalog entity."""
        url = f"{self.base_url}/api/v3/catalog/{entity_id}/collaboration/tag"
        resp = self.session.post(url, json=tags_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # SQL operations
    # ------------------------------------------------------------------

    def run_sql(self, sql, context=None):
        """Submit a SQL query and return the job ID."""
        url = f"{self.base_url}/api/v3/sql"
        payload = {"sql": sql}
        if context:
            payload["context"] = context
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_job_results(self, job_id, offset=0, limit=100):
        """Get results for a completed SQL job."""
        url = f"{self.base_url}/api/v3/job/{job_id}/results"
        params = {"offset": offset, "limit": limit}
        resp = self.session.get(url, params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
