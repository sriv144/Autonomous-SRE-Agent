import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Verify the health endpoint returns 200 OK."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}

@pytest.mark.asyncio
async def test_receive_alerts_valid():
    """Verify that a valid AlertManager payload is accepted."""
    payload = {
        "version": "4",
        "groupKey": "{}:{alertname=\"TestAlert\"}",
        "status": "firing",
        "receiver": "webhook",
        "groupLabels": {"alertname": "TestAlert"},
        "commonLabels": {"severity": "critical"},
        "commonAnnotations": {"summary": "Test Summary"},
        "externalURL": "http://alertmanager",
        "alerts": [
            {
                "status": "firing",
                "labels": {"alertname": "TestAlert", "instance": "demo"},
                "annotations": {"description": "Something is wrong"},
                "startsAt": "2023-01-01T12:00:00Z",
                "endsAt": "2023-01-01T13:00:00Z"
            }
        ]
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/alerts", json=payload)
    
    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "message": "Alerts queued for processing"}

@pytest.mark.asyncio
async def test_receive_alerts_invalid():
    """Verify that invalid payloads are rejected (422 Unprocessable Entity)."""
    payload = {"invalid": "data"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/alerts", json=payload)
    
    assert response.status_code == 422
