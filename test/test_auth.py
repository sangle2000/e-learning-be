from fastapi.testclient import TestClient


def test_signup_success(client: TestClient) -> None:
    """
    Registers a new user successfully.
    """
    signup_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "username": "John Doe"
    }
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["email"] == signup_data["email"]
    assert data["full_name"] == signup_data["username"]
    assert data["is_active"] is True
    assert "password" not in data


def test_signup_duplicate_email_fails(client: TestClient) -> None:
    """
    Checks that registering a duplicate email returns HTTP 400.
    """
    signup_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "username": "First User"
    }
    # First sign up
    response = client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 201
    
    # Try again with same email
    response_dup = client.post("/api/v1/auth/signup", json=signup_data)
    assert response_dup.status_code == 400
    assert "already exists" in response_dup.json()["detail"]


def test_signin_success(client: TestClient) -> None:
    """
    Verifies that a user can sign in and obtain a JWT bearer token.
    """
    # Create the user first
    signup_data = {
        "email": "login@example.com",
        "password": "mypassword123",
        "username": "Test User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)
    
    # Attempt login
    login_data = {
        "email": "login@example.com",
        "password": "mypassword123"
    }
    response = client.post("/api/v1/auth/signin", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_signin_wrong_password_fails(client: TestClient) -> None:
    """
    Verifies that logging in with an invalid password returns HTTP 400.
    """
    # Create user
    signup_data = {
        "email": "wrong_pass@example.com",
        "password": "correct_password",
        "username": "Test User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)
    
    # Invalid password attempt
    login_data = {
        "email": "wrong_pass@example.com",
        "password": "incorrect_password"
    }
    response = client.post("/api/v1/auth/signin", json=login_data)
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_signin_non_existent_user_fails(client: TestClient) -> None:
    """
    Verifies that logging in with a non-existent email returns HTTP 400.
    """
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    response = client.post("/api/v1/auth/signin", json=login_data)
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_refresh_token_success(client: TestClient) -> None:
    """
    Verifies that the /refresh endpoint can issue a new set of tokens.
    """
    # 1. Create a user
    signup_data = {
        "email": "refresh@example.com",
        "password": "mypassword123",
        "username": "Refresh User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)

    # 2. Login to get tokens
    login_data = {
        "email": "refresh@example.com",
        "password": "mypassword123"
    }
    login_res = client.post("/api/v1/auth/signin", json=login_data)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "accessToken" in tokens
    assert "refreshToken" in tokens
    refresh_token = tokens["refreshToken"]

    # 3. Refresh token
    refresh_res = client.post("/api/v1/auth/refresh", json={"refreshToken": refresh_token})
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "accessToken" in new_tokens
    assert "refreshToken" in new_tokens
    assert new_tokens["accessToken"] != tokens["accessToken"]


def test_refresh_token_invalid_fails(client: TestClient) -> None:
    """
    Verifies that an invalid refresh token is rejected with HTTP 401.
    """
    refresh_res = client.post("/api/v1/auth/refresh", json={"refreshToken": "invalid_refresh_token_hash"})
    assert refresh_res.status_code == 401
    assert "Invalid refresh token" in refresh_res.json()["detail"]


def test_token_lifetimes(client: TestClient) -> None:
    """
    Verifies that accessToken has ~1 hour lifetime and refreshToken has ~1 week lifetime.
    """
    import jwt
    from app.core.config import settings
    from app.core import security
    from datetime import datetime, timezone

    # 1. Create and Login user
    signup_data = {
        "email": "lifetime@example.com",
        "password": "mypassword123",
        "username": "Lifetime User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)

    login_data = {
        "email": "lifetime@example.com",
        "password": "mypassword123"
    }
    res = client.post("/api/v1/auth/signin", json=login_data)
    assert res.status_code == 200
    tokens = res.json()
    
    # 2. Decode access token
    access_payload = jwt.decode(
        tokens["accessToken"], settings.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    # 3. Decode refresh token
    refresh_payload = jwt.decode(
        tokens["refreshToken"], settings.SECRET_KEY, algorithms=[security.ALGORITHM]
    )

    now = datetime.now(timezone.utc).timestamp()
    
    # Check access token exp is ~1 hour (3600 seconds)
    access_lifetime = access_payload["exp"] - now
    # It should be close to 3600 seconds, let's allow a margin of 10 seconds
    assert 3580 < access_lifetime < 3620

    # Check refresh token exp is ~1 week (7 days = 604800 seconds)
    refresh_lifetime = refresh_payload["exp"] - now
    assert 604700 < refresh_lifetime < 604900


def test_get_me_success(client: TestClient) -> None:
    """
    Verifies that an authenticated user can fetch their own profile.
    """
    # 1. Create a user
    signup_data = {
        "email": "me@example.com",
        "password": "mypassword123",
        "username": "Me User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)

    # 2. Login to get token
    login_data = {
        "email": "me@example.com",
        "password": "mypassword123"
    }
    res = client.post("/api/v1/auth/signin", json=login_data)
    assert res.status_code == 200
    token = res.json()["accessToken"]

    # 3. Call GET /me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "me@example.com"
    assert me_data["full_name"] == "Me User"


def test_get_me_unauthorized(client: TestClient) -> None:
    """
    Verifies that calling GET /me without a token fails with HTTP 401.
    """
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_refresh_token_fails(client: TestClient) -> None:
    """
    Verifies that calling GET /me using a refreshToken instead of an accessToken fails with HTTP 403.
    """
    # 1. Create a user
    signup_data = {
        "email": "merefresh@example.com",
        "password": "mypassword123",
        "username": "Me Refresh User"
    }
    client.post("/api/v1/auth/signup", json=signup_data)

    # 2. Login to get token
    login_data = {
        "email": "merefresh@example.com",
        "password": "mypassword123"
    }
    res = client.post("/api/v1/auth/signin", json=login_data)
    assert res.status_code == 200
    refresh_token = res.json()["refreshToken"]

    # 3. Call GET /me with refreshToken
    headers = {"Authorization": f"Bearer {refresh_token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 403
    assert "Could not validate credentials" in me_res.json()["detail"]
