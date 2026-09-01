from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_project_or_404(
    db: Session,
    project_id: int,
) -> Project:
    project = ProjectService.get_project(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Creates a new project for Earned Value Management analysis.",
)
def create_project(
    project_data: ProjectCreate,
    db: DatabaseSession,
) -> Project:
    return ProjectService.create_project(
        db,
        project_data,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List projects",
    description="Returns all registered projects.",
)
def get_projects(
    db: DatabaseSession,
) -> list[Project]:
    return ProjectService.get_projects(db)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project",
    description="Returns a project by its identifier.",
)
def get_project(
    project_id: int,
    db: DatabaseSession,
) -> Project:
    return get_project_or_404(
        db,
        project_id,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description="Updates an existing project.",
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: DatabaseSession,
) -> Project:
    project = get_project_or_404(
        db,
        project_id,
    )

    return ProjectService.update_project(
        db,
        project,
        project_data,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Deletes an existing project.",
)
def delete_project(
    project_id: int,
    db: DatabaseSession,
) -> Response:
    project = get_project_or_404(
        db,
        project_id,
    )

    ProjectService.delete_project(
        db,
        project,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )