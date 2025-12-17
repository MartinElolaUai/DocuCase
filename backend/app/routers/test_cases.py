from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from math import ceil
from app.database import get_db
from app.models import TestCase, Feature, GherkinStep, GherkinSubStep
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, UpdateStepsRequest
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


@router.get("")
def get_test_cases(
    feature_id: Optional[str] = Query(None, alias="featureId"),
    application_id: Optional[str] = Query(None, alias="applicationId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    type_filter: Optional[str] = Query(None, alias="type"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test cases with pagination."""
    query = db.query(TestCase)
    
    if feature_id:
        query = query.filter(TestCase.feature_id == feature_id)
    if application_id:
        query = query.join(Feature).filter(Feature.application_id == application_id)
    if status_filter:
        query = query.filter(TestCase.status == status_filter)
    if type_filter:
        query = query.filter(TestCase.type == type_filter)
    if priority_filter:
        query = query.filter(TestCase.priority == priority_filter)
    if search:
        query = query.filter(
            or_(
                TestCase.name.ilike(f"%{search}%"),
                TestCase.description.ilike(f"%{search}%"),
                TestCase.scenario_name.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    test_cases = query.order_by(TestCase.updated_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
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
            "featureId": tc.feature_id,
            "azureUserStoryId": tc.azure_user_story_id,
            "azureUserStoryUrl": tc.azure_user_story_url,
            "azureTestCaseId": tc.azure_test_case_id,
            "azureTestCaseUrl": tc.azure_test_case_url,
            "tags": tc.tags or [],
            "scenarioName": tc.scenario_name,
            "createdAt": tc.created_at.isoformat(),
            "updatedAt": tc.updated_at.isoformat(),
            "feature": {
                "id": tc.feature.id,
                "name": tc.feature.name,
                "application": {
                    "id": tc.feature.application.id,
                    "name": tc.feature.application.name,
                    "group": {
                        "id": tc.feature.application.group.id,
                        "name": tc.feature.application.group.name
                    }
                }
            },
            "_count": {
                "steps": len(tc.steps),
                "pipelineResults": len(tc.pipeline_results)
            },
            "pipelineResults": [latest_result] if latest_result else []
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


@router.get("/{test_case_id}")
def get_test_case(
    test_case_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    # Build steps with sub-steps
    steps = []
    for step in sorted(tc.steps, key=lambda x: x.order):
        sub_steps = [
            {"id": sub.id, "text": sub.text, "order": sub.order}
            for sub in sorted(step.sub_steps, key=lambda x: x.order)
        ]
        steps.append({
            "id": step.id,
            "type": step.type.value,
            "text": step.text,
            "order": step.order,
            "subSteps": sub_steps
        })
    
    # Build pipeline results
    pipeline_results = []
    for pr in sorted(tc.pipeline_results, key=lambda x: x.created_at, reverse=True)[:10]:
        pipeline_results.append({
            "id": pr.id,
            "status": pr.status.value,
            "details": pr.details,
            "logUrl": pr.log_url,
            "duration": pr.duration,
            "createdAt": pr.created_at.isoformat(),
            "pipeline": {
                "id": pr.pipeline.id,
                "gitlabPipelineId": pr.pipeline.gitlab_pipeline_id,
                "branch": pr.pipeline.branch,
                "status": pr.pipeline.status.value,
                "webUrl": pr.pipeline.web_url
            }
        })
    
    return {
        "success": True,
        "data": {
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "type": tc.type.value,
            "priority": tc.priority.value,
            "status": tc.status.value,
            "featureId": tc.feature_id,
            "azureUserStoryId": tc.azure_user_story_id,
            "azureUserStoryUrl": tc.azure_user_story_url,
            "azureTestCaseId": tc.azure_test_case_id,
            "azureTestCaseUrl": tc.azure_test_case_url,
            "tags": tc.tags or [],
            "scenarioName": tc.scenario_name,
            "createdAt": tc.created_at.isoformat(),
            "updatedAt": tc.updated_at.isoformat(),
            "feature": {
                "id": tc.feature.id,
                "name": tc.feature.name,
                "application": {
                    "id": tc.feature.application.id,
                    "name": tc.feature.application.name,
                    "group": {
                        "id": tc.feature.application.group.id,
                        "name": tc.feature.application.group.name
                    }
                }
            },
            "steps": steps,
            "pipelineResults": pipeline_results
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_test_case(
    tc_data: TestCaseCreate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new test case."""
    feature = db.query(Feature).filter(Feature.id == tc_data.feature_id).first()
    
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature no encontrada"
        )
    
    new_tc = TestCase(
        name=tc_data.name,
        description=tc_data.description,
        type=tc_data.type,
        priority=tc_data.priority,
        status=tc_data.status,
        feature_id=tc_data.feature_id,
        azure_user_story_id=tc_data.azure_user_story_id,
        azure_user_story_url=tc_data.azure_user_story_url,
        azure_test_case_id=tc_data.azure_test_case_id,
        azure_test_case_url=tc_data.azure_test_case_url,
        tags=tc_data.tags or [],
        scenario_name=tc_data.scenario_name
    )
    
    db.add(new_tc)
    db.commit()
    db.refresh(new_tc)
    
    # Create steps if provided
    if tc_data.steps:
        for idx, step_data in enumerate(tc_data.steps):
            step = GherkinStep(
                test_case_id=new_tc.id,
                type=step_data.type,
                text=step_data.text,
                order=step_data.order or idx + 1
            )
            db.add(step)
            db.commit()
            db.refresh(step)
            
            if step_data.sub_steps:
                for sub_idx, sub_data in enumerate(step_data.sub_steps):
                    sub_step = GherkinSubStep(
                        step_id=step.id,
                        text=sub_data.text,
                        order=sub_data.order or sub_idx + 1
                    )
                    db.add(sub_step)
        
        db.commit()
    
    # Reload to get steps
    db.refresh(new_tc)
    
    steps = []
    for step in sorted(new_tc.steps, key=lambda x: x.order):
        sub_steps = [
            {"id": sub.id, "text": sub.text, "order": sub.order}
            for sub in sorted(step.sub_steps, key=lambda x: x.order)
        ]
        steps.append({
            "id": step.id,
            "type": step.type.value,
            "text": step.text,
            "order": step.order,
            "subSteps": sub_steps
        })
    
    return {
        "success": True,
        "data": {
            "id": new_tc.id,
            "name": new_tc.name,
            "description": new_tc.description,
            "type": new_tc.type.value,
            "priority": new_tc.priority.value,
            "status": new_tc.status.value,
            "featureId": new_tc.feature_id,
            "tags": new_tc.tags or [],
            "scenarioName": new_tc.scenario_name,
            "createdAt": new_tc.created_at.isoformat(),
            "feature": {"id": feature.id, "name": feature.name},
            "steps": steps
        }
    }


@router.put("/{test_case_id}")
def update_test_case(
    test_case_id: str,
    tc_data: TestCaseUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    if tc_data.name:
        tc.name = tc_data.name
    if tc_data.description is not None:
        tc.description = tc_data.description
    if tc_data.type:
        tc.type = tc_data.type
    if tc_data.priority:
        tc.priority = tc_data.priority
    if tc_data.status:
        tc.status = tc_data.status
    if tc_data.feature_id:
        feature = db.query(Feature).filter(Feature.id == tc_data.feature_id).first()
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature no encontrada"
            )
        tc.feature_id = tc_data.feature_id
    if tc_data.azure_user_story_id is not None:
        tc.azure_user_story_id = tc_data.azure_user_story_id
    if tc_data.azure_user_story_url is not None:
        tc.azure_user_story_url = tc_data.azure_user_story_url
    if tc_data.azure_test_case_id is not None:
        tc.azure_test_case_id = tc_data.azure_test_case_id
    if tc_data.azure_test_case_url is not None:
        tc.azure_test_case_url = tc_data.azure_test_case_url
    if tc_data.tags is not None:
        tc.tags = tc_data.tags
    if tc_data.scenario_name is not None:
        tc.scenario_name = tc_data.scenario_name
    
    db.commit()
    db.refresh(tc)
    
    return {
        "success": True,
        "data": {
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "type": tc.type.value,
            "priority": tc.priority.value,
            "status": tc.status.value,
            "featureId": tc.feature_id,
            "tags": tc.tags or [],
            "scenarioName": tc.scenario_name,
            "updatedAt": tc.updated_at.isoformat(),
            "feature": {"id": tc.feature.id, "name": tc.feature.name},
            "_count": {
                "steps": len(tc.steps),
                "pipelineResults": len(tc.pipeline_results)
            }
        }
    }


@router.delete("/{test_case_id}")
def delete_test_case(
    test_case_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    db.delete(tc)
    db.commit()
    
    return {
        "success": True,
        "message": "Caso de prueba eliminado exitosamente"
    }


@router.get("/{test_case_id}/steps")
def get_test_case_steps(
    test_case_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all steps of a test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    steps = []
    for step in sorted(tc.steps, key=lambda x: x.order):
        sub_steps = [
            {"id": sub.id, "text": sub.text, "order": sub.order}
            for sub in sorted(step.sub_steps, key=lambda x: x.order)
        ]
        steps.append({
            "id": step.id,
            "type": step.type.value,
            "text": step.text,
            "order": step.order,
            "subSteps": sub_steps
        })
    
    return {
        "success": True,
        "data": steps
    }


@router.put("/{test_case_id}/steps")
def update_test_case_steps(
    test_case_id: str,
    steps_data: UpdateStepsRequest,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update all steps of a test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    # Delete existing steps
    db.query(GherkinStep).filter(GherkinStep.test_case_id == test_case_id).delete()
    db.commit()
    
    # Create new steps
    for idx, step_data in enumerate(steps_data.steps):
        step = GherkinStep(
            test_case_id=test_case_id,
            type=step_data.type,
            text=step_data.text,
            order=step_data.order or idx + 1
        )
        db.add(step)
        db.commit()
        db.refresh(step)
        
        if step_data.sub_steps:
            for sub_idx, sub_data in enumerate(step_data.sub_steps):
                sub_step = GherkinSubStep(
                    step_id=step.id,
                    text=sub_data.text,
                    order=sub_data.order or sub_idx + 1
                )
                db.add(sub_step)
    
    db.commit()
    
    # Get updated steps
    db.refresh(tc)
    
    steps = []
    for step in sorted(tc.steps, key=lambda x: x.order):
        sub_steps = [
            {"id": sub.id, "text": sub.text, "order": sub.order}
            for sub in sorted(step.sub_steps, key=lambda x: x.order)
        ]
        steps.append({
            "id": step.id,
            "type": step.type.value,
            "text": step.text,
            "order": step.order,
            "subSteps": sub_steps
        })
    
    return {
        "success": True,
        "data": steps
    }


@router.get("/{test_case_id}/results")
def get_test_case_results(
    test_case_id: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pipeline results for a test case."""
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    if not tc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de prueba no encontrado"
        )
    
    results = []
    for pr in sorted(tc.pipeline_results, key=lambda x: x.created_at, reverse=True)[:limit]:
        results.append({
            "id": pr.id,
            "status": pr.status.value,
            "details": pr.details,
            "logUrl": pr.log_url,
            "duration": pr.duration,
            "createdAt": pr.created_at.isoformat(),
            "pipeline": {
                "id": pr.pipeline.id,
                "gitlabPipelineId": pr.pipeline.gitlab_pipeline_id,
                "branch": pr.pipeline.branch,
                "status": pr.pipeline.status.value,
                "webUrl": pr.pipeline.web_url
            }
        })
    
    return {
        "success": True,
        "data": results
    }

