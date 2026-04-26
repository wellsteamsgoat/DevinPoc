"""Health check endpoint."""

from flask_restx import Namespace, Resource

health_ns = Namespace("health", description="Health check operations")


@health_ns.route("")
class HealthCheck(Resource):
    """Simple health check."""

    def get(self):
        """Check if the API is running."""
        return {"status": "healthy", "service": "dremio-cloner"}
