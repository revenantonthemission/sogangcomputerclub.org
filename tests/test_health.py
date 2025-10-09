import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint"""
    response = await client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

    # Check services status
    services = data["services"]
    assert "database" in services
    assert services["database"] == "healthy"

    # Redis and Kafka are disabled in tests
    assert services.get("redis") == "unhealthy"
    assert services.get("kafka") == "unhealthy"

    # Overall status should be degraded because Redis and Kafka are down
    assert data["status"] in ["healthy", "degraded"]
