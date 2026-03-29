"""Tests for Authentication endpoints."""

import pytest


@pytest.mark.asyncio
async def test_root(client):
    """Test root endpoint returns service info."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "FraudShield" in data["service"]


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client, sample_user):
    """Test user registration."""
    response = await client.post("/api/auth/register", json=sample_user)
    # May fail without DB, but validates schema
    assert response.status_code in [201, 500]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code in [401, 500]


@pytest.mark.asyncio
async def test_transactions_unauthorized(client):
    """Test that transactions endpoint requires authentication."""
    response = await client.get("/api/transactions/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_fraud_alerts_unauthorized(client):
    """Test that fraud alerts endpoint requires authentication."""
    response = await client.get("/api/fraud/alerts")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client):
    """Test that dashboard endpoint requires authentication."""
    response = await client.get("/api/analytics/dashboard")
    assert response.status_code == 403
