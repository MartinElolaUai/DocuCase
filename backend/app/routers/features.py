from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from math import ceil
from app.database import get_db
from app.models import Feature, Application, TestCase
from app.schemas.feature import FeatureCreate, FeatureUpdate
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/features", tags=["features"])


@router.get("")
def get_features(
    application_id: Optional[str] = Query(None, alias="applicationId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all features with pagination."""
    query = db.query(Feature)
    
    if application_id:
        query = query.filter(Feature.application_id == application_id)
    if status_filter:
        query = query.filter(Feature.status == status_filter)
    if search:
        query = query.filter(
            or_(
                Feature.name.ilike(f"%{search}%"),
                Feature.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    features = query.order_by(Feature.name.asc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for feature in features:
        result.append({
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "featureFilePath": feature.feature_file_path,
            "status": feature.status.value,
            "applicationId": feature.application_id,
            "createdAt": feature.created_at.isoformat(),
            "updatedAt": feature.updated_at.isoformat(),
            "application": {
                "id": feature.application.id,
                "name": feature.application.name,
                "group": {
                    "id": feature.application.group.id,
                    "name": feature.application.group.name
                }
            },
            "_count": {"testCases": len(feature.test_cases)}
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


@router.get("/{feature_id}")
def get_feature(
    feature_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific feature."""
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature no encontrada"
        )
    
    test_cases = []
    for tc in sorted(feature.test_cases, key=lambda x: x.name):
        test_cases.append({
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "type": tc.type.value,
            "priority": tc.priority.value,
            "status": tc.status.value,
            "scenarioName": tc.scenario_name,
            "_count": {
                "steps": len(tc.steps),
                "pipelineResults": len(tc.pipeline_results)
            }
        })
    
    return {
        "success": True,
        "data": {
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "featureFilePath": feature.feature_file_path,
            "status": feature.status.value,
            "applicationId": feature.application_id,
            "createdAt": feature.created_at.isoformat(),
            "updatedAt": feature.updated_at.isoformat(),
            "application": {
                "id": feature.application.id,
                "name": feature.application.name,
                "group": {
                    "id": feature.application.group.id,
                    "name": feature.application.group.name
                }
            },
            "testCases": test_cases
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_feature(
    feature_data: FeatureCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new feature."""
    app = db.query(Application).filter(Application.id == feature_data.application_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )
    
    existing = db.query(Feature).filter(
        Feature.name == feature_data.name,
        Feature.application_id == feature_data.application_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una feature con ese nombre en la aplicación"
        )
    
    new_feature = Feature(
        name=feature_data.name,
        description=feature_data.description,
        feature_file_path=feature_data.feature_file_path,
        status=feature_data.status,
        application_id=feature_data.application_id
    )
    
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    
    return {
        "success": True,
        "data": {
            "id": new_feature.id,
            "name": new_feature.name,
            "description": new_feature.description,
            "featureFilePath": new_feature.feature_file_path,
            "status": new_feature.status.value,
            "applicationId": new_feature.application_id,
            "createdAt": new_feature.created_at.isoformat(),
            "application": {"id": app.id, "name": app.name},
            "_count": {"testCases": 0}
        }
    }


@router.put("/{feature_id}")
def update_feature(
    feature_id: str,
    feature_data: FeatureUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a feature."""
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature no encontrada"
        )
    
    if feature_data.name:
        feature.name = feature_data.name
    if feature_data.description is not None:
        feature.description = feature_data.description
    if feature_data.feature_file_path is not None:
        feature.feature_file_path = feature_data.feature_file_path
    if feature_data.status:
        feature.status = feature_data.status
    if feature_data.application_id:
        app = db.query(Application).filter(Application.id == feature_data.application_id).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aplicación no encontrada"
            )
        feature.application_id = feature_data.application_id
    
    db.commit()
    db.refresh(feature)
    
    return {
        "success": True,
        "data": {
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "featureFilePath": feature.feature_file_path,
            "status": feature.status.value,
            "applicationId": feature.application_id,
            "updatedAt": feature.updated_at.isoformat(),
            "application": {"id": feature.application.id, "name": feature.application.name},
            "_count": {"testCases": len(feature.test_cases)}
        }
    }


@router.delete("/{feature_id}")
def delete_feature(
    feature_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a feature."""
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature no encontrada"
        )
    
    if len(feature.test_cases) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una feature con casos de prueba asociados"
        )
    
    db.delete(feature)
    db.commit()
    
    return {
        "success": True,
        "message": "Feature eliminada exitosamente"
    }


@router.get("/{feature_id}/test-cases")
def get_feature_test_cases(
    feature_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test cases of a feature."""
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature no encontrada"
        )
    
    query = db.query(TestCase).filter(TestCase.feature_id == feature_id)
    
    if status_filter:
        query = query.filter(TestCase.status == status_filter)
    if type_filter:
        query = query.filter(TestCase.type == type_filter)
    
    test_cases = query.order_by(TestCase.name.asc()).all()
    
    result = []
    for tc in test_cases:
        # Get latest pipeline result
        latest_result = None
        if tc.pipeline_results:
            latest = sorted(tc.pipeline_results, key=lambda x: x.created_at, reverse=True)[0]
            latest_result = {
                "id": latest.id,
                "status": latest.status.value,
                "createdAt": latest.created_at.isoformat(),
                "pipeline": {
                    "id": latest.pipeline.id,
                    "gitlabPipelineId": latest.pipeline.gitlab_pipeline_id,
                    "branch": latest.pipeline.branch,
                    "status": latest.pipeline.status.value
                }
            }
        
        result.append({
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "type": tc.type.value,
            "priority": tc.priority.value,
            "status": tc.status.value,
            "scenarioName": tc.scenario_name,
            "_count": {
                "steps": len(tc.steps),
                "pipelineResults": len(tc.pipeline_results)
            },
            "pipelineResults": [latest_result] if latest_result else []
        })
    
    return {
        "success": True,
        "data": result
    }

