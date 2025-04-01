from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import time
from typing import Optional, Tuple

from app.db.database import get_db
from app.db.models import User
from app.core.config import settings
from app.schemas.token import TokenData

# Set up logger
logger = logging.getLogger(__name__)

# OAuth2 password bearer token URL path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Validates the JWT token and returns the current user.
    
    Args:
        token: JWT token from authorization header
        db: Database session
        
    Returns:
        User object of the authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user identifier from token
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
            
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token has expired")
            raise credentials_exception
            
        token_data = TokenData(email=email)
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        logger.warning(f"User not found: {token_data.email}")
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifies that the current user account is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    return current_user

def verify_program_active(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)) -> Tuple[User, bool]:
    """
    Verifies if user's 75 Hard program is active and returns program status.
    
    Returns:
        Tuple containing user object and boolean indicating if program is active
    """
    # Check if user has any progress entries
    from app.db.models import DailyProgress
    
    first_day = db.query(DailyProgress).filter(
        DailyProgress.user_id == user.id
    ).order_by(DailyProgress.day_number).first()
    
    last_day = db.query(DailyProgress).filter(
        DailyProgress.user_id == user.id
    ).order_by(DailyProgress.day_number.desc()).first()
    
    # If no progress entries, program hasn't started
    if not first_day:
        return user, False
    
    # Check if program is completed (all 75 days completed)
    if last_day and last_day.day_number >= 75:
        return user, False
    
    # Check for any incomplete days that are older than today
    # This would indicate a program failure and restart is needed
    today = datetime.now().date()
    failed_day = db.query(DailyProgress).filter(
        DailyProgress.user_id == user.id,
        DailyProgress.date < today,
        DailyProgress.completed == False
    ).first()
    
    if failed_day:
        return user, False
        
    return user, True

class RateLimiter:
    """
    Rate limiting implementation for API endpoints.
    Uses in-memory storage for simplicity, but in production you should
    use Redis or a similar distributed cache.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_records = {}
        
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if the client has exceeded rate limits."""
        now = time.time()
        
        # Clean old records
        if client_id in self.request_records:
            self.request_records[client_id] = [
                timestamp for timestamp in self.request_records[client_id]
                if now - timestamp < 60  # Keep records from last minute
            ]
        else:
            self.request_records[client_id] = []
            
        # Check rate limit
        if len(self.request_records[client_id]) >= self.requests_per_minute:
            return True
            
        # Record this request
        self.request_records[client_id].append(now)
        return False

# Create rate limiter instance
api_rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

def check_rate_limit(request: Request, user: User = Depends(get_current_active_user)):
    """
    Dependency for rate limiting API requests.
    
    Args:
        request: FastAPI request object
        user: Current authenticated user
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    client_id = str(user.id)  # Use user ID as client identifier
    
    if api_rate_limiter.is_rate_limited(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return user

def get_pagination(skip: int = 0, limit: int = 50) -> Tuple[int, int]:
    """
    Standardize pagination parameters across API endpoints.
    
    Args:
        skip: Number of items to skip (offset)
        limit: Maximum number of items to return
        
    Returns:
        Tuple of sanitized (skip, limit)
    """
    # Enforce reasonable limits
    if skip < 0:
        skip = 0
    
    # Cap the maximum items per request
    if limit <= 0 or limit > 100:
        limit = 50
        
    return skip, limit

def check_day_number(day_number: int):
    """
    Validate day number parameter for progress tracking.
    
    Args:
        day_number: Day number in the 75 Hard program
        
    Raises:
        HTTPException: If day number is invalid
    """
    if day_number < 1 or day_number > 75:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Day number must be between 1 and 75"
        )
    return day_number
