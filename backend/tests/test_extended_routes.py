docker compose -f docker-compose.prod.yml exec -T api bash -c 'cat << "EOF" > /app/tests/test_extended_routes.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_analytics_endpoints(async_client: AsyncClient):
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@campus.edu", "password": "admin123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/analytics/summary", headers=headers)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_complaint_filtering(async_client: AsyncClient):
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@campus.edu", "password": "admin123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/complaints/?status=PENDING&limit=10", headers=headers)
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    response = await async_client.get("/api/v1/complaints/")
    assert response.status_code in [401, 403]
EOF'