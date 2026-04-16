from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, desc, select

from renovaite.db import get_session
from renovaite.dependencies import current_user
from renovaite.models.project import Project
from renovaite.models.user import User
from renovaite.schemas.project import ProjectCreateIn, ProjectOut, ProjectUpdateIn

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_project_for_user(project_id: int, user: User, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.is_deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "Project not found.", "code": "NOT_FOUND"},
        )
    if project.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail={"error": "Forbidden.", "code": "FORBIDDEN"},
        )
    return project


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreateIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
) -> Project:
    assert user.id is not None
    project = Project(user_id=user.id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
) -> list[Project]:
    assert user.id is not None
    statement = (
        select(Project)
        .where(Project.user_id == user.id, Project.is_deleted == False)  # noqa: E712
        .order_by(desc(Project.created_at))
    )
    return list(db.exec(statement))


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
) -> Project:
    return _get_project_for_user(project_id, user, db)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdateIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
) -> Project:
    project = _get_project_for_user(project_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.now(UTC)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
) -> Response:
    project = _get_project_for_user(project_id, user, db)
    project.is_deleted = True
    project.updated_at = datetime.now(UTC)
    db.add(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
