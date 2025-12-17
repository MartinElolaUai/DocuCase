from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from math import ceil
from app.database import get_db
from app.models import Application, Group, Feature, TestRequest, TestCase
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("")
def get_applications(
    group_id: Optional[str] = Query(None, alias="groupId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all applications with pagination."""
    query = db.query(Application)
    
    if group_id:
        query = query.filter(Application.group_id == group_id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if search:
        query = query.filter(
            or_(
                Application.name.ilike(f"%{search}%"),
                Application.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    applications = query.order_by(Application.name.asc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "status": app.status.value,
            "groupId": app.group_id,
            "gitlabProjectId": app.gitlab_project_id,
            "gitlabProjectUrl": app.gitlab_project_url,
            "createdAt": app.created_at.isoformat(),
            "updatedAt": app.updated_at.isoformat(),
            "group": {
                "id": app.group.id,
                "name": app.group.name
            },
            "_count": {
                "features": len(app.features),
                "testRequests": len(app.test_requests)
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


@router.get("/{app_id}")
def get_application(
    app_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific application."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    features = []
    for feature in sorted(app.features, key=lambda x: x.name):
        features.append({
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "status": feature.status.value,
            "featureFilePath": feature.feature_file_path,
            "createdAt": feature.created_at.isoformat(),
            "_count": {"testCases": len(feature.test_cases)}
        })
    
    return {
        "success": True,
        "data": {
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "status": app.status.value,
            "groupId": app.group_id,
            "gitlabProjectId": app.gitlab_project_id,
            "gitlabProjectUrl": app.gitlab_project_url,
            "createdAt": app.created_at.isoformat(),
            "updatedAt": app.updated_at.isoformat(),
            "group": {
                "id": app.group.id,
                "name": app.group.name,
                "description": app.group.description
            },
            "features": features,
            "_count": {
                "features": len(app.features),
                "testRequests": len(app.test_requests)
            }
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_application(
    app_data: ApplicationCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new application."""
    group = db.query(Group).filter(Group.id == app_data.group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agrupador no encontrado"
        )
    
    existing_app = db.query(Application).filter(
        Application.name == app_data.name,
        Application.group_id == app_data.group_id
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una aplicación con ese nombre en el agrupador"
        )
    
    new_app = Application(
        name=app_data.name,
        description=app_data.description,
        group_id=app_data.group_id,
        gitlab_project_id=app_data.gitlab_project_id,
        gitlab_project_url=app_data.gitlab_project_url
    )
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return {
        "success": True,
        "data": {
            "id": new_app.id,
            "name": new_app.name,
            "description": new_app.description,
            "status": new_app.status.value,
            "groupId": new_app.group_id,
            "gitlabProjectId": new_app.gitlab_project_id,
            "gitlabProjectUrl": new_app.gitlab_project_url,
            "createdAt": new_app.created_at.isoformat(),
            "group": {"id": group.id, "name": group.name},
            "_count": {"features": 0}
        }
    }


@router.put("/{app_id}")
def update_application(
    app_id: str,
    app_data: ApplicationUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an application."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    if app_data.name:
        app.name = app_data.name
    if app_data.description is not None:
        app.description = app_data.description
    if app_data.status:
        app.status = app_data.status
    if app_data.group_id:
        group = db.query(Group).filter(Group.id == app_data.group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agrupador no encontrado"
            )
        app.group_id = app_data.group_id
    if app_data.gitlab_project_id is not None:
        app.gitlab_project_id = app_data.gitlab_project_id
    if app_data.gitlab_project_url is not None:
        app.gitlab_project_url = app_data.gitlab_project_url
    
    db.commit()
    db.refresh(app)
    
    return {
        "success": True,
        "data": {
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "status": app.status.value,
            "groupId": app.group_id,
            "gitlabProjectId": app.gitlab_project_id,
            "gitlabProjectUrl": app.gitlab_project_url,
            "updatedAt": app.updated_at.isoformat(),
            "group": {"id": app.group.id, "name": app.group.name},
            "_count": {"features": len(app.features)}
        }
    }


@router.delete("/{app_id}")
def delete_application(
    app_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an application."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    if len(app.features) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una aplicación con features asociadas"
        )
    
    db.delete(app)
    db.commit()
    
    return {
        "success": True,
        "message": "Aplicación eliminada exitosamente"
    }


@router.get("/{app_id}/features")
def get_application_features(
    app_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all features of an application."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    query = db.query(Feature).filter(Feature.application_id == app_id)
    
    if status_filter:
        query = query.filter(Feature.status == status_filter)
    
    features = query.order_by(Feature.name.asc()).all()
    
    result = []
    for feature in features:
        result.append({
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "status": feature.status.value,
            "featureFilePath": feature.feature_file_path,
            "createdAt": feature.created_at.isoformat(),
            "_count": {"testCases": len(feature.test_cases)}
        })
    
    return {
        "success": True,
        "data": result
    }


@router.get("/{app_id}/stats")
def get_application_stats(
    app_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for an application."""
    app = db.query(Application).filter(Application.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    # Feature stats by status
    feature_stats = db.query(
        Feature.status, func.count(Feature.id)
    ).filter(
        Feature.application_id == app_id
    ).group_by(Feature.status).all()
    
    # Test case stats by status
    test_case_stats = db.query(
        TestCase.status, func.count(TestCase.id)
    ).join(Feature).filter(
        Feature.application_id == app_id
    ).group_by(TestCase.status).all()
    
    # Request stats by status
    request_stats = db.query(
        TestRequest.status, func.count(TestRequest.id)
    ).filter(
        TestRequest.application_id == app_id
    ).group_by(TestRequest.status).all()
    
    return {
        "success": True,
        "data": {
            "features": [{"status": s.value, "count": c} for s, c in feature_stats],
            "testCases": [{"status": s.value, "count": c} for s, c in test_case_stats],
            "requests": [{"status": s.value, "count": c} for s, c in request_stats]
        }
    }

