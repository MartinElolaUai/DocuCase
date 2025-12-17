from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from math import ceil
from datetime import datetime
from app.database import get_db
from app.models import GitlabPipeline, TestCasePipelineResult, TestCase, PipelineStatus, TestCaseResultStatus
from app.schemas.pipeline import RegisterPipelineResult
from app.middleware.auth import get_current_user, AuthUser

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("")
def get_pipelines(
    gitlab_project_id: Optional[str] = Query(None, alias="gitlabProjectId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    branch: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pipelines with pagination."""
    query = db.query(GitlabPipeline)
    
    if gitlab_project_id:
        query = query.filter(GitlabPipeline.gitlab_project_id == gitlab_project_id)
    if status_filter:
        query = query.filter(GitlabPipeline.status == status_filter)
    if branch:
        query = query.filter(GitlabPipeline.branch.ilike(f"%{branch}%"))
    
    total = query.count()
    total_pages = ceil(total / limit)
    
    pipelines = query.order_by(GitlabPipeline.executed_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for pipeline in pipelines:
        result.append({
            "id": pipeline.id,
            "gitlabProjectId": pipeline.gitlab_project_id,
            "gitlabPipelineId": pipeline.gitlab_pipeline_id,
            "branch": pipeline.branch,
            "status": pipeline.status.value,
            "webUrl": pipeline.web_url,
            "executedAt": pipeline.executed_at.isoformat(),
            "createdAt": pipeline.created_at.isoformat(),
            "_count": {"testCaseResults": len(pipeline.test_case_results)}
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


@router.get("/{pipeline_id}")
def get_pipeline(
    pipeline_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific pipeline."""
    pipeline = db.query(GitlabPipeline).filter(GitlabPipeline.id == pipeline_id).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline no encontrado"
        )
    
    test_case_results = []
    for result in sorted(pipeline.test_case_results, key=lambda x: x.created_at, reverse=True):
        test_case_results.append({
            "id": result.id,
            "status": result.status.value,
            "details": result.details,
            "logUrl": result.log_url,
            "duration": result.duration,
            "createdAt": result.created_at.isoformat(),
            "testCase": {
                "id": result.test_case.id,
                "name": result.test_case.name,
                "scenarioName": result.test_case.scenario_name,
                "feature": {
                    "id": result.test_case.feature.id,
                    "name": result.test_case.feature.name,
                    "application": {
                        "id": result.test_case.feature.application.id,
                        "name": result.test_case.feature.application.name
                    }
                }
            }
        })
    
    return {
        "success": True,
        "data": {
            "id": pipeline.id,
            "gitlabProjectId": pipeline.gitlab_project_id,
            "gitlabPipelineId": pipeline.gitlab_pipeline_id,
            "branch": pipeline.branch,
            "status": pipeline.status.value,
            "webUrl": pipeline.web_url,
            "executedAt": pipeline.executed_at.isoformat(),
            "createdAt": pipeline.created_at.isoformat(),
            "testCaseResults": test_case_results
        }
    }


@router.post("/sync")
def sync_pipelines(
    project_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync pipelines from GitLab (placeholder)."""
    return {
        "success": True,
        "message": "Sincronización de pipelines iniciada",
        "data": {
            "projectId": project_id,
            "status": "pending"
        }
    }


@router.get("/{pipeline_id}/results")
def get_pipeline_results(
    pipeline_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get results for a specific pipeline."""
    pipeline = db.query(GitlabPipeline).filter(GitlabPipeline.id == pipeline_id).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline no encontrado"
        )
    
    results = []
    for result in sorted(pipeline.test_case_results, key=lambda x: x.created_at):
        results.append({
            "id": result.id,
            "status": result.status.value,
            "details": result.details,
            "logUrl": result.log_url,
            "duration": result.duration,
            "createdAt": result.created_at.isoformat(),
            "testCase": {
                "id": result.test_case.id,
                "name": result.test_case.name,
                "scenarioName": result.test_case.scenario_name,
                "feature": {
                    "id": result.test_case.feature.id,
                    "name": result.test_case.feature.name
                }
            }
        })
    
    # Calculate summary
    summary = {
        "total": len(results),
        "passed": len([r for r in pipeline.test_case_results if r.status == TestCaseResultStatus.PASSED]),
        "failed": len([r for r in pipeline.test_case_results if r.status == TestCaseResultStatus.FAILED]),
        "skipped": len([r for r in pipeline.test_case_results if r.status == TestCaseResultStatus.SKIPPED]),
        "notExecuted": len([r for r in pipeline.test_case_results if r.status == TestCaseResultStatus.NOT_EXECUTED])
    }
    
    return {
        "success": True,
        "data": {
            "results": results,
            "summary": summary
        }
    }


@router.post("/results")
def register_pipeline_result(
    data: RegisterPipelineResult,
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register pipeline result from CI/CD."""
    # Find or create pipeline
    pipeline = db.query(GitlabPipeline).filter(
        GitlabPipeline.gitlab_project_id == data.gitlab_project_id,
        GitlabPipeline.gitlab_pipeline_id == data.gitlab_pipeline_id
    ).first()
    
    if pipeline:
        # Update existing pipeline
        pipeline.status = data.pipeline_status or PipelineStatus.PASSED
        pipeline.branch = data.branch or "main"
        if data.web_url:
            pipeline.web_url = data.web_url
    else:
        # Create new pipeline
        pipeline = GitlabPipeline(
            gitlab_project_id=data.gitlab_project_id,
            gitlab_pipeline_id=data.gitlab_pipeline_id,
            branch=data.branch or "main",
            status=data.pipeline_status or PipelineStatus.PASSED,
            web_url=data.web_url,
            executed_at=data.executed_at or datetime.utcnow()
        )
        db.add(pipeline)
        db.commit()
        db.refresh(pipeline)
    
    # Register test results
    if data.test_results:
        for result_data in data.test_results:
            test_case = None
            
            if result_data.test_case_id:
                test_case = db.query(TestCase).filter(TestCase.id == result_data.test_case_id).first()
            elif result_data.scenario_name:
                test_case = db.query(TestCase).filter(
                    func.lower(TestCase.scenario_name) == result_data.scenario_name.lower()
                ).first()
            
            if test_case:
                # Find or create result
                existing_result = db.query(TestCasePipelineResult).filter(
                    TestCasePipelineResult.test_case_id == test_case.id,
                    TestCasePipelineResult.pipeline_id == pipeline.id
                ).first()
                
                if existing_result:
                    existing_result.status = result_data.status or TestCaseResultStatus.NOT_EXECUTED
                    if result_data.details:
                        existing_result.details = result_data.details
                    if result_data.log_url:
                        existing_result.log_url = result_data.log_url
                    if result_data.duration:
                        existing_result.duration = result_data.duration
                else:
                    new_result = TestCasePipelineResult(
                        test_case_id=test_case.id,
                        pipeline_id=pipeline.id,
                        status=result_data.status or TestCaseResultStatus.NOT_EXECUTED,
                        details=result_data.details,
                        log_url=result_data.log_url,
                        duration=result_data.duration
                    )
                    db.add(new_result)
    
    db.commit()
    db.refresh(pipeline)
    
    return {
        "success": True,
        "data": {
            "id": pipeline.id,
            "gitlabProjectId": pipeline.gitlab_project_id,
            "gitlabPipelineId": pipeline.gitlab_pipeline_id,
            "branch": pipeline.branch,
            "status": pipeline.status.value,
            "webUrl": pipeline.web_url,
            "executedAt": pipeline.executed_at.isoformat()
        }
    }

