from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError
from core.Models.user.user_model import User
import jwt

from sqlite.database import get_db
from sqlite.config import setting

security = HTTPBearer(scheme_name="Bearer")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                     db: Session = Depends(get_db)):
    
    token = credentials.credentials

    try: 
        payload = jwt.decode(token,
                             setting.JWT_SECRET_KEY,
                             algorithms=[setting.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found in token")
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token type")

        try:
            user_id = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, invalid user_id format in token",
            )
        
        user_obj = db.query(User).filter(User.id == user_id).first()
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, user not found",
            )
        
        return user_obj

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, token has expired",
        )
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, token decode failed",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {e}",
        )


def generate_access_token(user_id: int, expire_in: int | None = None):
    now = datetime.utcnow()
    exp_access = expire_in or setting.EXPIRE_IN_ACCESS_TOKEN
    payload = {
        "type" : "access",
        "user_id" : str(user_id),
        "iat" : now,
        "exp" : now + timedelta(seconds=exp_access)
    }

    return  jwt.encode(payload,
                       setting.JWT_SECRET_KEY,
                       algorithm=setting.JWT_ALGORITHM)


def generate_refresh_token(user_id: int, expire_in: int | None = None):
    now = datetime.utcnow()
    exp_refresh = expire_in or setting.EXPIRE_IN_REFRESH_TOKEN
    payload = {
        "type" : "refresh",
        "user_id" : str(user_id),
        "iat" : now,
        "exp" : now + timedelta(seconds=exp_refresh)
    }

    return jwt.encode(payload,
                      setting.JWT_SECRET_KEY,
                      algorithm=setting.JWT_ALGORITHM)




def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            setting.JWT_SECRET_KEY,
            algorithms=[setting.JWT_ALGORITHM],
        )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, user_id not found in token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed, token type is not refresh",
            )

        return int(user_id)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, refresh token has expired",
        )
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, token decode failed",
        )
    