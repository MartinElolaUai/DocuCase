from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from math import ceil
from datetime import datetime
from app.database import get_db
from app.models import TestRequest, Application
from app.schemas.test_request import TestRequestCreate, TestRequestUpdate, TestRequestStatusUpdate
from app.middleware.auth import get_current_user, AuthUser
from app.services.notification_service import send_notification

router = APIRouter(prefix="/test-requests", tags=["test-requests"])


@router.get("")
def get_test_requests(
    application_id: Optional[str] = Query(None, alias="applicationId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    requester_id: Optional[str] = Query(None, alias="requesterId"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all test requests with pagination."""
    query = db.query(TestRequest)
    
    if application_id:
        query = query.filter(TestRequest.application_id == application_id)
    if status_filter:
        query = query.filter(TestRequest.status == status_filter)
    if requester_id:
        query = query.filter(TestRequest.requester_id == requester_id)
    if search:
        query = query.filter(
            or_(
                TestRequest.title.ilike(f"%{search}%"),
                TestRequest.description.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    requests = query.order_by(TestRequest.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for req in requests:
        assignee = None
        if req.assignee:
            assignee = {
                "id": req.assignee.id,
                "firstName": req.assignee.first_name,
                "lastName": req.assignee.last_name,
                "email": req.assignee.email
            }
        
        generated_tc = None
        if req.generated_test_case:
            generated_tc = {
                "id": req.generated_test_case.id,
                "name": req.generated_test_case.name,
                "status": req.generated_test_case.status.value
            }
        
        result.append({
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "status": req.status.value,
            "applicationId": req.application_id,
            "requesterId": req.requester_id,
            "assigneeId": req.assignee_id,
            "azureWorkItemId": req.azure_work_item_id,
            "azureWorkItemUrl": req.azure_work_item_url,
            "additionalNotes": req.additional_notes,
            "generatedTestCaseId": req.generated_test_case_id,
            "type": req.type.value,
            "environment": req.environment,
            "hasAuth": req.has_auth,
            "authType": req.auth_type,
            "authUsers": req.auth_users,
            "frontPlan": req.front_plan,
            "apiPlan": req.api_plan,
            "createdAt": req.created_at.isoformat(),
            "updatedAt": req.updated_at.isoformat(),
            "application": {
                "id": req.application.id,
                "name": req.application.name,
                "group": {
                    "id": req.application.group.id,
                    "name": req.application.group.name
                }
            },
            "requester": {
                "id": req.requester.id,
                "firstName": req.requester.first_name,
                "lastName": req.requester.last_name,
                "email": req.requester.email
            },
            "assignee": assignee,
            "generatedTestCase": generated_tc
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


@router.get("/my")
def get_my_test_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's test requests."""
    query = db.query(TestRequest).filter(TestRequest.requester_id == current_user.id)
    
    if status_filter:
        query = query.filter(TestRequest.status == status_filter)
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    requests = query.order_by(TestRequest.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for req in requests:
        assignee = None
        if req.assignee:
            assignee = {
                "id": req.assignee.id,
                "firstName": req.assignee.first_name,
                "lastName": req.assignee.last_name,
                "email": req.assignee.email
            }
        
        generated_tc = None
        if req.generated_test_case:
            generated_tc = {
                "id": req.generated_test_case.id,
                "name": req.generated_test_case.name,
                "status": req.generated_test_case.status.value
            }
        
        result.append({
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "status": req.status.value,
            "applicationId": req.application_id,
            "createdAt": req.created_at.isoformat(),
            "updatedAt": req.updated_at.isoformat(),
            "application": {
                "id": req.application.id,
                "name": req.application.name,
                "group": {
                    "id": req.application.group.id,
                    "name": req.application.group.name
                }
            },
            "assignee": assignee,
            "generatedTestCase": generated_tc
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


@router.get("/{request_id}")
def get_test_request(
    request_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific test request."""
    req = db.query(TestRequest).filter(TestRequest.id == request_id).first()
    
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    assignee = None
    if req.assignee:
        assignee = {
            "id": req.assignee.id,
            "firstName": req.assignee.first_name,
            "lastName": req.assignee.last_name,
            "email": req.assignee.email
        }
    
    generated_tc = None
    if req.generated_test_case:
        generated_tc = {
            "id": req.generated_test_case.id,
            "name": req.generated_test_case.name,
            "status": req.generated_test_case.status.value,
            "feature": {
                "id": req.generated_test_case.feature.id,
                "name": req.generated_test_case.feature.name
            },
            "_count": {"steps": len(req.generated_test_case.steps)}
        }
    
    return {
        "success": True,
        "data": {
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "status": req.status.value,
            "applicationId": req.application_id,
            "requesterId": req.requester_id,
            "assigneeId": req.assignee_id,
            "azureWorkItemId": req.azure_work_item_id,
            "azureWorkItemUrl": req.azure_work_item_url,
            "additionalNotes": req.additional_notes,
            "generatedTestCaseId": req.generated_test_case_id,
            "createdAt": req.created_at.isoformat(),
            "updatedAt": req.updated_at.isoformat(),
            "application": {
                "id": req.application.id,
                "name": req.application.name,
                "group": {
                    "id": req.application.group.id,
                    "name": req.application.group.name
                }
            },
            "requester": {
                "id": req.requester.id,
                "firstName": req.requester.first_name,
                "lastName": req.requester.last_name,
                "email": req.requester.email
            },
            "assignee": assignee,
            "type": req.type.value,
            "environment": req.environment,
            "hasAuth": req.has_auth,
            "authType": req.auth_type,
            "authUsers": req.auth_users,
            "frontPlan": req.front_plan,
            "apiPlan": req.api_plan,
            "generatedTestCase": generated_tc
        }
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_test_request(
    req_data: TestRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new test request."""
    try:
        app = db.query(Application).filter(Application.id == req_data.application_id).first()
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aplicación no encontrada"
            )
        
        new_request = TestRequest(
            title=req_data.title,
            description=req_data.description,
            application_id=req_data.application_id,
            requester_id=current_user.id,
            azure_work_item_id=req_data.azure_work_item_id,
            azure_work_item_url=req_data.azure_work_item_url,
            additional_notes=req_data.additional_notes,
            status="NEW",
            type=req_data.type,
            environment=req_data.environment,
            has_auth=bool(req_data.has_auth) if req_data.has_auth is not None else False,
            auth_type=req_data.auth_type,
            auth_users=req_data.auth_users,
            front_plan=req_data.front_plan,
            api_plan=req_data.api_plan,
        )
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
    except Exception as e:
        db.rollback()
        print(f"Error creating test request: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear solicitud: {str(e)}"
        )
    
    # Send notification in background
    background_tasks.add_task(
        send_notification,
        db,
        "request_new",
        app.group_id,
        {
            "request": {
                "id": new_request.id,
                "title": new_request.title,
                "description": new_request.description
            },
            "application": {
                "id": app.id,
                "name": app.name
            },
            "requester": {
                "first_name": current_user.first_name,
                "last_name": current_user.last_name
            }
        }
    )
    
    return {
        "success": True,
        "data": {
            "id": new_request.id,
            "title": new_request.title,
            "description": new_request.description,
            "status": new_request.status.value,
            "applicationId": new_request.application_id,
            "requesterId": new_request.requester_id,
            "createdAt": new_request.created_at.isoformat(),
            "application": {"id": app.id, "name": app.name},
            "requester": {
                "id": current_user.id,
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "email": current_user.email
            }
        }
    }


@router.put("/{request_id}")
def update_test_request(
    request_id: str,
    req_data: TestRequestUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a test request."""
    req = db.query(TestRequest).filter(TestRequest.id == request_id).first()
    
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    if req_data.title:
        req.title = req_data.title
    if req_data.description:
        req.description = req_data.description
    if req_data.status:
        req.status = req_data.status
    if req_data.assignee_id is not None:
        req.assignee_id = req_data.assignee_id if req_data.assignee_id else None
    if req_data.azure_work_item_id is not None:
        req.azure_work_item_id = req_data.azure_work_item_id
    if req_data.azure_work_item_url is not None:
        req.azure_work_item_url = req_data.azure_work_item_url
    if req_data.additional_notes is not None:
        req.additional_notes = req_data.additional_notes
    if req_data.generated_test_case_id is not None:
        req.generated_test_case_id = req_data.generated_test_case_id if req_data.generated_test_case_id else None
    if req_data.type is not None:
        req.type = req_data.type
    if req_data.environment is not None:
        req.environment = req_data.environment
    if req_data.has_auth is not None:
        req.has_auth = bool(req_data.has_auth)
    if req_data.auth_type is not None:
        req.auth_type = req_data.auth_type
    if req_data.auth_users is not None:
        req.auth_users = req_data.auth_users
    if req_data.front_plan is not None:
        req.front_plan = req_data.front_plan
    if req_data.api_plan is not None:
        req.api_plan = req_data.api_plan
    
    db.commit()
    db.refresh(req)
    
    assignee = None
    if req.assignee:
        assignee = {
            "id": req.assignee.id,
            "firstName": req.assignee.first_name,
            "lastName": req.assignee.last_name,
            "email": req.assignee.email
        }
    
    generated_tc = None
    if req.generated_test_case:
        generated_tc = {
            "id": req.generated_test_case.id,
            "name": req.generated_test_case.name,
            "status": req.generated_test_case.status.value
        }
    
    return {
        "success": True,
        "data": {
            "id": req.id,
            "title": req.title,
            "description": req.description,
            "status": req.status.value,
            "applicationId": req.application_id,
            "requesterId": req.requester_id,
            "assigneeId": req.assignee_id,
            "updatedAt": req.updated_at.isoformat(),
            "application": {"id": req.application.id, "name": req.application.name},
            "requester": {
                "id": req.requester.id,
                "firstName": req.requester.first_name,
                "lastName": req.requester.last_name,
                "email": req.requester.email
            },
            "assignee": assignee,
            "generatedTestCase": generated_tc
        }
    }


@router.patch("/{request_id}/status")
async def update_test_request_status(
    request_id: str,
    status_data: TestRequestStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a test request status."""
    req = db.query(TestRequest).filter(TestRequest.id == request_id).first()
    
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    previous_status = req.status.value
    req.status = status_data.status
    
    if status_data.assignee_id:
        req.assignee_id = status_data.assignee_id
    if status_data.generated_test_case_id:
        req.generated_test_case_id = status_data.generated_test_case_id
    if status_data.notes:
        timestamp = datetime.utcnow().isoformat()
        note_text = f"[{timestamp}] {status_data.notes}"
        if req.additional_notes:
            req.additional_notes = f"{req.additional_notes}\n\n{note_text}"
        else:
            req.additional_notes = note_text
    
    db.commit()
    db.refresh(req)
    
    # Send notification in background
    background_tasks.add_task(
        send_notification,
        db,
        "request_status_change",
        req.application.group_id,
        {
            "request": {
                "id": req.id,
                "title": req.title,
                "requester": {
                    "email": req.requester.email
                }
            },
            "previousStatus": previous_status,
            "newStatus": status_data.status.value
        }
    )
    
    assignee = None
    if req.assignee:
        assignee = {
            "id": req.assignee.id,
            "firstName": req.assignee.first_name,
            "lastName": req.assignee.last_name,
            "email": req.assignee.email
        }
    
    generated_tc = None
    if req.generated_test_case:
        generated_tc = {
            "id": req.generated_test_case.id,
            "name": req.generated_test_case.name,
            "status": req.generated_test_case.status.value
        }
    
    return {
        "success": True,
        "data": {
            "id": req.id,
            "title": req.title,
            "status": req.status.value,
            "updatedAt": req.updated_at.isoformat(),
            "application": {"id": req.application.id, "name": req.application.name},
            "requester": {
                "id": req.requester.id,
                "firstName": req.requester.first_name,
                "lastName": req.requester.last_name,
                "email": req.requester.email
            },
            "assignee": assignee,
            "generatedTestCase": generated_tc
        }
    }


@router.delete("/{request_id}")
def delete_test_request(
    request_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a test request."""
    req = db.query(TestRequest).filter(TestRequest.id == request_id).first()
    
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    db.delete(req)
    db.commit()
    
    return {
        "success": True,
        "message": "Solicitud eliminada exitosamente"
    }

