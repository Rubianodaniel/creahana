import pytest


@pytest.mark.asyncio
async def test_register_user(test_client):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser", 
        "password": "testpassword123"
    }
    
    response = await test_client.post("/api/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["is_active"] is True
    assert "id" in data
    # Password should not be returned
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_login_success(test_client):
    """Test successful login."""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "username": "loginuser", 
        "password": "loginpass123"
    }
    
    register_response = await test_client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # Now login
    login_data = {
        "email": "login@example.com",
        "password": "loginpass123"
    }
    
    response = await test_client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = await test_client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(test_client):
    """Test getting current user info with valid token."""
    # First register and login a user
    user_data = {
        "email": "current@example.com",
        "username": "currentuser", 
        "password": "currentpass123"
    }
    
    register_response = await test_client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    login_data = {
        "email": "current@example.com",
        "password": "currentpass123"
    }
    
    login_response = await test_client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Get current user info
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "current@example.com"
    assert data["username"] == "currentuser"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_client):
    """Test getting current user info with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await test_client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client):
    """Test registering with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1", 
        "password": "pass123"
    }
    
    # First registration should succeed
    response1 = await test_client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    user_data2 = {
        "email": "duplicate@example.com",
        "username": "user2", 
        "password": "pass456"
    }
    
    response2 = await test_client.post("/api/auth/register", json=user_data2)
    assert response2.status_code == 400
    assert "duplicate@example.com" in response2.json()["detail"].lower()