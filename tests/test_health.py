import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["services"]["database"] == "healthy"
    assert data["services"]["redis"] == "healthy"
    assert data["services"]["kafka"] == "healthy"
