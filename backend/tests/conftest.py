"""
Backend Tests — Configuration and Fixtures
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing."""
    return {
        "amount": 149.62,
        "time": 406.0,
        "v1": -1.3598,
        "v2": -0.0728,
        "v3": 2.5363,
        "v4": 1.3782,
        "v5": -0.3383,
        "v6": 0.4624,
        "v7": 0.2396,
        "v8": 0.0987,
        "v9": 0.3638,
        "v10": 0.0908,
        "v11": -0.5516,
        "v12": -0.6178,
        "v13": -0.9913,
        "v14": -0.3112,
        "v15": 1.4682,
        "v16": -0.4704,
        "v17": 0.2080,
        "v18": 0.0258,
        "v19": 0.4039,
        "v20": 0.2514,
        "v21": -0.0183,
        "v22": 0.2778,
        "v23": -0.1105,
        "v24": 0.0669,
        "v25": 0.1285,
        "v26": -0.1891,
        "v27": 0.1336,
        "v28": -0.0211,
    }


@pytest.fixture
def sample_user():
    """Sample user registration data."""
    return {
        "email": "analyst@fraudshield.ai",
        "full_name": "Test Analyst",
        "password": "SecurePass123!",
        "role": "analyst",
    }
