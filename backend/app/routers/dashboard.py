from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import (
    Group, Application, Feature, TestCase, TestRequest,
    GitlabPipeline, TestCasePipelineResult
)
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    # Basic counts
    total_groups = db.query(Group).count()
    total_applications = db.query(Application).filter(Application.status == "ACTIVE").count()
    total_features = db.query(Feature).count()
    total_test_cases = db.query(TestCase).count()
    total_requests = db.query(TestRequest).count()
    pending_requests = db.query(TestRequest).filter(TestRequest.status == "NEW").count()
    
    # Recent pipelines (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_pipelines = db.query(GitlabPipeline).filter(
        GitlabPipeline.executed_at >= seven_days_ago
    ).count()
    
    # Test cases by status
    test_cases_by_status = db.query(
        TestCase.status, func.count(TestCase.id)
    ).group_by(TestCase.status).all()
    
    # Requests by status
    requests_by_status = db.query(
        TestRequest.status, func.count(TestRequest.id)
    ).group_by(TestRequest.status).all()
    
    return {
        "success": True,
        "data": {
            "overview": {
                "totalGroups": total_groups,
                "totalApplications": total_applications,
                "totalFeatures": total_features,
                "totalTestCases": total_test_cases,
                "totalRequests": total_requests,
                "pendingRequests": pending_requests,
                "recentPipelines": recent_pipelines
            },
            "testCasesByStatus": [
                {"status": s.value, "count": c} for s, c in test_cases_by_status
            ],
            "requestsByStatus": [
                {"status": s.value, "count": c} for s, c in requests_by_status
            ]
        }
    }


@router.get("/activity")
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activity."""
    # Recent test cases
    recent_test_cases = db.query(TestCase).order_by(
        TestCase.updated_at.desc()
    ).limit(limit).all()
    
    test_cases_data = []
    for tc in recent_test_cases:
        test_cases_data.append({
            "id": tc.id,
            "name": tc.name,
            "status": tc.status.value,
            "updatedAt": tc.updated_at.isoformat(),
            "feature": {
                "name": tc.feature.name,
                "application": {"name": tc.feature.application.name}
            }
        })
    
    # Recent requests
    recent_requests = db.query(TestRequest).order_by(
        TestRequest.updated_at.desc()
    ).limit(limit).all()
    
    requests_data = []
    for req in recent_requests:
        requests_data.append({
            "id": req.id,
            "title": req.title,
            "status": req.status.value,
            "updatedAt": req.updated_at.isoformat(),
            "application": {"name": req.application.name},
            "requester": {
                "firstName": req.requester.first_name,
                "lastName": req.requester.last_name
            }
        })
    
    # Recent pipelines
    recent_pipelines = db.query(GitlabPipeline).order_by(
        GitlabPipeline.executed_at.desc()
    ).limit(5).all()
    
    pipelines_data = []
    for pipeline in recent_pipelines:
        pipelines_data.append({
            "id": pipeline.id,
            "gitlabPipelineId": pipeline.gitlab_pipeline_id,
            "branch": pipeline.branch,
            "status": pipeline.status.value,
            "executedAt": pipeline.executed_at.isoformat(),
            "webUrl": pipeline.web_url
        })
    
    return {
        "success": True,
        "data": {
            "testCases": test_cases_data,
            "requests": requests_data,
            "pipelines": pipelines_data
        }
    }


@router.get("/test-cases-stats")
def get_test_cases_stats(
    application_id: Optional[str] = Query(None, alias="applicationId"),
    group_id: Optional[str] = Query(None, alias="groupId"),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get test cases statistics by status, type, and priority."""
    query = db.query(TestCase)
    
    if application_id:
        query = query.join(Feature).filter(Feature.application_id == application_id)
    elif group_id:
        query = query.join(Feature).join(Application).filter(Application.group_id == group_id)
    
    # By status
    by_status = db.query(
        TestCase.status, func.count(TestCase.id)
    )
    if application_id:
        by_status = by_status.join(Feature).filter(Feature.application_id == application_id)
    elif group_id:
        by_status = by_status.join(Feature).join(Application).filter(Application.group_id == group_id)
    by_status = by_status.group_by(TestCase.status).all()
    
    # By type
    by_type = db.query(
        TestCase.type, func.count(TestCase.id)
    )
    if application_id:
        by_type = by_type.join(Feature).filter(Feature.application_id == application_id)
    elif group_id:
        by_type = by_type.join(Feature).join(Application).filter(Application.group_id == group_id)
    by_type = by_type.group_by(TestCase.type).all()
    
    # By priority
    by_priority = db.query(
        TestCase.priority, func.count(TestCase.id)
    )
    if application_id:
        by_priority = by_priority.join(Feature).filter(Feature.application_id == application_id)
    elif group_id:
        by_priority = by_priority.join(Feature).join(Application).filter(Application.group_id == group_id)
    by_priority = by_priority.group_by(TestCase.priority).all()
    
    return {
        "success": True,
        "data": {
            "byStatus": [{"status": s.value, "count": c} for s, c in by_status],
            "byType": [{"type": t.value, "count": c} for t, c in by_type],
            "byPriority": [{"priority": p.value, "count": c} for p, c in by_priority]
        }
    }


@router.get("/pipeline-stats")
def get_pipeline_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pipeline statistics for a period."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Pipelines by status
    pipelines_by_status = db.query(
        GitlabPipeline.status, func.count(GitlabPipeline.id)
    ).filter(
        GitlabPipeline.executed_at >= start_date
    ).group_by(GitlabPipeline.status).all()
    
    # Test results by status
    test_results_by_status = db.query(
        TestCasePipelineResult.status, func.count(TestCasePipelineResult.id)
    ).filter(
        TestCasePipelineResult.created_at >= start_date
    ).group_by(TestCasePipelineResult.status).all()
    
    # Recent pipelines
    recent_pipelines = db.query(GitlabPipeline).filter(
        GitlabPipeline.executed_at >= start_date
    ).order_by(GitlabPipeline.executed_at.desc()).limit(20).all()
    
    pipelines_data = []
    for pipeline in recent_pipelines:
        pipelines_data.append({
            "id": pipeline.id,
            "gitlabPipelineId": pipeline.gitlab_pipeline_id,
            "branch": pipeline.branch,
            "status": pipeline.status.value,
            "executedAt": pipeline.executed_at.isoformat(),
            "webUrl": pipeline.web_url,
            "_count": {"testCaseResults": len(pipeline.test_case_results)}
        })
    
    return {
        "success": True,
        "data": {
            "pipelinesByStatus": [
                {"status": s.value, "count": c} for s, c in pipelines_by_status
            ],
            "testResultsByStatus": [
                {"status": s.value, "count": c} for s, c in test_results_by_status
            ],
            "recentPipelines": pipelines_data
        }
    }

