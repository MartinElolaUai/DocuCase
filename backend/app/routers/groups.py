from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from math import ceil
from app.database import get_db
from app.models import Group, GroupSubscription, Application
from app.schemas.group import GroupCreate, GroupUpdate
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("")
def get_groups(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups with pagination."""
    query = db.query(Group)
    
    if search:
        query = query.filter(
            or_(
                Group.name.ilike(f"%{search}%"),
                Group.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    groups = query.order_by(Group.name.asc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for group in groups:
        active_apps = [
            {"id": app.id, "name": app.name, "status": app.status.value}
            for app in group.applications
            if app.status.value == "ACTIVE"
        ]
        
        result.append({
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "createdAt": group.created_at.isoformat(),
            "updatedAt": group.updated_at.isoformat(),
            "applications": active_apps,
            "_count": {
                "applications": len(group.applications),
                "subscriptions": len(group.subscriptions)
            }
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


@router.get("/{group_id}")
def get_group(
    group_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    applications = []
    for app in sorted(group.applications, key=lambda x: x.name):
        applications.append({
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "status": app.status.value,
            "createdAt": app.created_at.isoformat(),
            "_count": {"features": len(app.features)}
        })
    
    subscriptions = []
    for sub in group.subscriptions:
        subscriptions.append({
            "id": sub.id,
            "user": {
                "id": sub.user.id,
                "firstName": sub.user.first_name,
                "lastName": sub.user.last_name,
                "email": sub.user.email
            }
        })
    
    return {
        "success": True,
        "data": {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "createdAt": group.created_at.isoformat(),
            "updatedAt": group.updated_at.isoformat(),
            "applications": applications,
            "subscriptions": subscriptions
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_group(
    group_data: GroupCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group."""
    existing_group = db.query(Group).filter(Group.name == group_data.name).first()
    
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un agrupador con ese nombre"
        )
    
    new_group = Group(
        name=group_data.name,
        description=group_data.description
    )
    
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    
    return {
        "success": True,
        "data": {
            "id": new_group.id,
            "name": new_group.name,
            "description": new_group.description,
            "createdAt": new_group.created_at.isoformat(),
            "updatedAt": new_group.updated_at.isoformat(),
            "_count": {"applications": 0, "subscriptions": 0}
        }
    }


@router.put("/{group_id}")
def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    if group_data.name and group_data.name != group.name:
        existing = db.query(Group).filter(Group.name == group_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un agrupador con ese nombre"
            )
        group.name = group_data.name
    
    if group_data.description is not None:
        group.description = group_data.description
    
    db.commit()
    db.refresh(group)
    
    return {
        "success": True,
        "data": {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "createdAt": group.created_at.isoformat(),
            "updatedAt": group.updated_at.isoformat(),
            "_count": {
                "applications": len(group.applications),
                "subscriptions": len(group.subscriptions)
            }
        }
    }


@router.delete("/{group_id}")
def delete_group(
    group_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    if len(group.applications) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un agrupador con aplicaciones asociadas"
        )
    
    db.delete(group)
    db.commit()
    
    return {
        "success": True,
        "message": "Agrupador eliminado exitosamente"
    }


@router.get("/{group_id}/subscribers")
def get_group_subscribers(
    group_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscribers of a group."""
    group = db.query(Group).filter(Group.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    subscribers = []
    for sub in group.subscriptions:
        subscribers.append({
            "id": sub.id,
            "createdAt": sub.created_at.isoformat(),
            "user": {
                "id": sub.user.id,
                "firstName": sub.user.first_name,
                "lastName": sub.user.last_name,
                "email": sub.user.email,
                "role": sub.user.role.value
            }
        })
    
    return {
        "success": True,
        "data": subscribers
    }

