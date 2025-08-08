async def create_test_user_and_login(client, email="test@example.com", username="testuser", password="testpass123"):
    """
    Helper function to create a user and get auth token.
    Returns the authorization headers.
    """
    # Register user
    user_data = {
        "email": email,
        "username": username,
        "password": password
    }
    
    register_response = await client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": email,
        "password": password
    }
    
    login_response = await client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Return headers
    return {"Authorization": f"Bearer {token}"}


async def create_test_user_and_get_headers(client, user_num=1):
    """
    Create a unique test user and return auth headers.
    """
    return await create_test_user_and_login(
        client,
        email=f"user{user_num}@example.com",
        username=f"user{user_num}",
        password=f"pass{user_num}123"
    )