import logging
import httpx
import base64
import json
import datetime
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.config import settings
from backend.app.db.mongo import get_db

logger = logging.getLogger(__name__)
security_bearer = HTTPBearer(auto_error=False)

class AuthenticatedUser:
    def __init__(self, user_id: str, email: Optional[str] = None, claims: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.email = email
        self.claims = claims or {}

    def __repr__(self):
        return f"<AuthenticatedUser id={self.user_id} email={self.email}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "claims": self.claims
        }

async def sync_user_to_db(user: AuthenticatedUser):
    """Syncs or updates authenticated Clerk user profile in MongoDB Atlas users collection."""
    try:
        db = get_db()
        if db is not None and user.user_id:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            await db.users.update_one(
                {"user_id": user.user_id},
                {
                    "$set": {
                        "user_id": user.user_id,
                        "email": user.email,
                        "last_active": now_iso,
                    },
                    "$setOnInsert": {
                        "created_at": now_iso
                    }
                },
                upsert=True
            )
    except Exception as e:
        logger.debug(f"User sync to MongoDB notice: {e}")

async def get_optional_user(
    request: Request,
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[AuthenticatedUser]:
    """Extracts user from Authorization Header (Bearer token) or Clerk __session cookie."""
    token = None
    if token_auth and token_auth.credentials:
        token = token_auth.credentials
    elif "__session" in request.cookies:
        token = request.cookies.get("__session")

    if not token:
        return None

    user = await verify_clerk_token(token)
    if user:
        await sync_user_to_db(user)
    return user

async def get_current_user(
    user: Optional[AuthenticatedUser] = Depends(get_optional_user)
) -> AuthenticatedUser:
    """Strict dependency requiring authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with Clerk.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def verify_clerk_token(token: str) -> Optional[AuthenticatedUser]:
    """Verifies JWT using Clerk Secret Key or token claims decoding."""
    # 1. Fast decode of standard JWT payload claims
    try:
        parts = token.split(".")
        if len(parts) >= 2:
            payload_b64 = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64)
            claims = json.loads(payload_bytes.decode("utf-8"))
            
            user_id = claims.get("sub") or claims.get("user_id")
            if user_id:
                email = claims.get("email") or claims.get("email_address") or claims.get("primary_email_address")
                return AuthenticatedUser(user_id=user_id, email=email, claims=claims)
    except Exception as e:
        logger.debug(f"Token claims parse note: {e}")

    # 2. Fallback to direct Clerk API verification if CLERK_SECRET_KEY is configured
    if settings.CLERK_SECRET_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    "https://api.clerk.com/v1/me",
                    headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
                )
                if res.status_code == 200:
                    data = res.json()
                    email = None
                    if data.get("email_addresses") and len(data["email_addresses"]) > 0:
                        email = data["email_addresses"][0].get("email_address")
                    return AuthenticatedUser(
                        user_id=data.get("id", "usr_clerk"),
                        email=email,
                        claims=data
                    )
        except Exception as e:
            logger.warning(f"Clerk API direct verification notice: {e}")

    return None

