import uuid
import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from app.core import database as db
from app.core import security
from app.schema.auth import UserRegister, UserResponse, UserLogin, TokenResponse, RefreshTokenRequest
from app.deps import get_current_user

router = APIRouter()

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def signup(user_in: UserRegister) -> UserResponse:
    """
    Registers a new user inside the local JSON database.
    Checks for email conflicts, hashes the password, and returns public profile info.
    """
    existing_user = db.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    # Prepare user data
    hashed_password = security.get_password_hash(user_in.password)
    user_id = str(uuid.uuid4())
    
    new_user_data = {
        "id": user_id,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "full_name": user_in.username,
        "is_active": True,
        "accessToken": None,
        "refreshToken": None,
    }

    # Save to JSON database
    db.create_user(new_user_data)
    
    return UserResponse(
        id=user_id,
        email=user_in.email,
        full_name=user_in.username,
        is_active=True
    )


@router.post(
    "/signin",
    response_model=TokenResponse,
    summary="Log in and retrieve token",
)
def signin(credentials: UserLogin) -> TokenResponse:
    """
    Logs in an existing user.
    Validates email/password and returns a JWT bearer access token.
    """
    user = db.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not security.verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Generate JWT tokens
    access_token = security.create_access_token(subject=user["id"])
    refresh_token = security.create_refresh_token(subject=user["id"])

    # Temporarily store tokens in the json file (database)
    users = db.load_users()
    for u in users:
        if u["id"] == user["id"]:
            u["accessToken"] = access_token
            u["refreshToken"] = refresh_token
            break
    db.save_users(users)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        accessToken=access_token,
        refreshToken=refresh_token
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
def refresh(payload: RefreshTokenRequest) -> TokenResponse:
    """
    Refreshes the access token using a valid refresh token.
    Checks the token status in the JSON database.
    """
    try:
        decoded = jwt.decode(
            payload.refreshToken, security.settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = decoded.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    users = db.load_users()
    user = next((u for u in users if u.get("id") == user_id), None)
    if not user or user.get("refreshToken") != payload.refreshToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or invalid",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Generate new tokens
    access_token = security.create_access_token(subject=user["id"])
    refresh_token = security.create_refresh_token(subject=user["id"])

    # Update tokens in the json database
    user["accessToken"] = access_token
    user["refreshToken"] = refresh_token
    db.save_users(users)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        accessToken=access_token,
        refreshToken=refresh_token
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Returns the authenticated user's profile information.
    """
    return current_user
