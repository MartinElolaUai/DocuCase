from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from math import ceil
from app.database import get_db
from app.models import User, Group, GroupSubscription, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import hash_password
from app.middleware.auth import get_current_user, get_current_admin_user, AuthUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/subscriptions")
def get_user_subscriptions(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's group subscriptions."""
    subscriptions = db.query(GroupSubscription).filter(
        GroupSubscription.user_id == current_user.id
    ).all()
    
    result = []
    for sub in subscriptions:
        applications = [
            {"id": app.id, "name": app.name}
            for app in sub.group.applications
            if app.status.value == "ACTIVE"
        ]
        result.append({
            "id": sub.id,
            "group": {
                "id": sub.group.id,
                "name": sub.group.name,
                "applications": applications
            }
        })
    
    return {
        "success": True,
        "data": result
    }


@router.post("/subscriptions/{group_id}", status_code=status.HTTP_201_CREATED)
def subscribe_to_group(
    group_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    existing_sub = db.query(GroupSubscription).filter(
        GroupSubscription.user_id == current_user.id,
        GroupSubscription.group_id == group_id
    ).first()
    
    if existing_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya estás suscrito a este agrupador"
        )
    
    subscription = GroupSubscription(
        user_id=current_user.id,
        group_id=group_id
    )
    
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    return {
        "success": True,
        "data": {
            "id": subscription.id,
            "group": {
                "id": group.id,
                "name": group.name
            }
        }
    }


@router.delete("/subscriptions/{group_id}")
def unsubscribe_from_group(
    group_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from a group."""
    subscription = db.query(GroupSubscription).filter(
        GroupSubscription.user_id == current_user.id,
        GroupSubscription.group_id == group_id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No estás suscrito a este agrupador"
        )
    
    db.delete(subscription)
    db.commit()
    
    return {
        "success": True,
        "message": "Suscripción eliminada exitosamente"
    }


@router.get("")
def get_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if search:
        query = query.filter(
            or_(
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for user in users:
        subscriptions = [{
            "id": sub.id,
            "group": {"id": sub.group.id, "name": sub.group.name}
        } for sub in user.subscriptions]
        
        result.append({
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": user.role.value,
            "status": user.status.value,
            "createdAt": user.created_at.isoformat(),
            "updatedAt": user.updated_at.isoformat(),
            "subscriptions": subscriptions
        })
    
    return {
        "success": True,
        "data": result,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": total_pages
        }
    }


@router.get("/{user_id}")
def get_user(
    user_id: str,
    current_user: AuthUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    subscriptions = [{
        "id": sub.id,
        "group": {"id": sub.group.id, "name": sub.group.name}
    } for sub in user.subscriptions]
    
    test_requests = []
    for req in user.test_requests[:10]:
        test_requests.append({
            "id": req.id,
            "title": req.title,
            "status": req.status.value,
            "application": {"id": req.application.id, "name": req.application.name}
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
            "updatedAt": user.updated_at.isoformat(),
            "subscriptions": subscriptions,
            "testRequests": test_requests
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: AuthUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
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
        role=user_data.role or UserRole.USER,
        status=user_data.status or UserStatus.ACTIVE
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "data": {
            "id": new_user.id,
            "email": new_user.email,
            "firstName": new_user.first_name,
            "lastName": new_user.last_name,
            "role": new_user.role.value,
            "status": new_user.status.value,
            "createdAt": new_user.created_at.isoformat()
        }
    }


@router.put("/{user_id}")
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: AuthUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user_data.email:
        existing = db.query(User).filter(
            User.email == user_data.email.lower(),
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
        user.email = user_data.email.lower()
    
    if user_data.first_name:
        user.first_name = user_data.first_name
    if user_data.last_name:
        user.last_name = user_data.last_name
    if user_data.role:
        user.role = user_data.role
    if user_data.status:
        user.status = user_data.status
    if user_data.password:
        user.password = hash_password(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": user.role.value,
            "status": user.status.value,
            "updatedAt": user.updated_at.isoformat()
        }
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    current_user: AuthUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": "Usuario eliminado exitosamente"
    }

