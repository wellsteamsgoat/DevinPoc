from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from app.routes.health import health_ns
from app.routes.catalog import catalog_ns
from app.routes.clone import clone_ns


def create_app():
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version="1.0",
        title="Dremio Cloner API",
        description=(
            "A Flask API for cloning Dremio resources (spaces, folders, "
            "virtual datasets, reflections, wikis, and tags) from a source "
            "Dremio instance to a target Dremio instance. Use the Swagger UI "
            "below to interact with the endpoints."
        ),
        doc="/swagger",
    )

    api.add_namespace(health_ns, path="/api/health")
    api.add_namespace(catalog_ns, path="/api/catalog")
    api.add_namespace(clone_ns, path="/api/clone")

    return app
