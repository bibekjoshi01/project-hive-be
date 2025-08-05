from enum import Enum
import random
from app.utils.casing import CamelBaseModel
from typing import Optional, List
from pydantic import Field


class CategoryOut(CamelBaseModel):
    id: int
    name: str


class DepartmentOut(CamelBaseModel):
    id: int
    name: str


class BatchYearOut(CamelBaseModel):
    id: int
    year: int


class ProjectResponse(CamelBaseModel):
    id: int
    title: str
    slug: str
    abstract: str
    level: str
    supervisor: str
    technologies_used: str
    github_link: Optional[str]
    documentation_link: Optional[str]
    status: str
    submitted_at: str
    submitted_by_full_name: str
    category: CategoryOut
    department: DepartmentOut
    batch_year: BatchYearOut
    rating_average: float = Field(default=5.0)
    views: int = Field(default=0)


class ProjectList(CamelBaseModel):
    count: int
    results: List[ProjectResponse]


class ProjectTeamMemberOut(CamelBaseModel):
    id: int
    full_name: str
    roll_no: str
    photo: Optional[str]


class ProjectFileOut(CamelBaseModel):
    id: int
    file_type: str
    file: str


class ProjectRetrieveResponse(CamelBaseModel):
    id: int
    title: str
    slug: str
    abstract: str
    level: str
    supervisor: str
    technologies_used: List[str]
    github_links: List[str]
    documentation_link: Optional[str]
    project_details: Optional[str]
    status: str
    submitted_at: str
    submitted_by_full_name: str
    category: CategoryOut
    department: DepartmentOut
    batch_year: BatchYearOut
    rating_average: float = Field(default=5.0)
    total_ratings: int = Field(default=0)
    team_members: List[ProjectTeamMemberOut]
    files: List[ProjectFileOut]
    views: int = Field(default_factory=lambda: random.randint(0, 500))


class ProjectStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ProjectApprovalPayload(CamelBaseModel):
    project_id: int
    status: ProjectStatus
