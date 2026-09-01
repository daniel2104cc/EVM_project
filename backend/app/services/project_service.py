from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    def create_project(
        db: Session,
        project_data: ProjectCreate,
    ) -> Project:
        project = Project(
            name=project_data.name,
            description=project_data.description,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def get_projects(db: Session) -> list[Project]:
        statement = select(Project).order_by(Project.id)

        return list(db.scalars(statement).all())

    @staticmethod
    def get_project(
        db: Session,
        project_id: int,
    ) -> Project | None:
        return db.get(Project, project_id)

    @staticmethod
    def update_project(
        db: Session,
        project: Project,
        project_data: ProjectUpdate,
    ) -> Project:
        project.name = project_data.name
        project.description = project_data.description

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(
        db: Session,
        project: Project,
    ) -> None:
        db.delete(project)
        db.commit()