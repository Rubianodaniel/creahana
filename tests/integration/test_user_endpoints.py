import pytest


@pytest.mark.asyncio
async def test_create_user_simple(test_client):
    """Test basic user creation."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser"
    }
    
    response = await test_client.post("/api/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_get_user_simple(test_client):
    """Test basic user retrieval."""
    # Create user first
    user_data = {"email": "get@example.com", "username": "getuser"}
    create_response = await test_client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Get the user
    response = await test_client.get(f"/api/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]