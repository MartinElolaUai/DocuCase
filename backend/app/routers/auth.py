from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserStatus
from app.schemas.user import UserLogin, UserCreate, ChangePassword
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo. Contacte al administrador."
        )
    
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    token = create_access_token(user.id)
    
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "role": user.role.value,
            }
        }
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email.lower(),
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role or "USER",
        status=user_data.status or "ACTIVE"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(new_user.id)
    
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "firstName": new_user.first_name,
                "lastName": new_user.last_name,
                "role": new_user.role.value,
            }
        }
    }


@router.get("/me")
def get_me(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    subscriptions = []
    for sub in user.subscriptions:
        subscriptions.append({
            "id": sub.id,
            "group": {
                "id": sub.group.id,
                "name": sub.group.name
            }
        })
    
    return {
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": user.role.value,
            "status": user.status.value,
            "createdAt": user.created_at.isoformat(),
            "subscriptions": subscriptions
        }
    }


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not verify_password(data.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    user.password = hash_password(data.new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Contraseña actualizada exitosamente"
    }

