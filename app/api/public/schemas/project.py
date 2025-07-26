from pydantic import Field, HttpUrl
from typing import List, Optional
import random
from enum import Enum

from app.utils.casing import CamelBaseModel


class CategoryResponse(CamelBaseModel):
    id: int
    name: str
    project_count: int


class CategoryList(CamelBaseModel):
    count: int
    results: List[CategoryResponse]


class DepartmentResponse(CamelBaseModel):
    id: int
    name: str


class DepartmentList(CamelBaseModel):
    count: int
    results: List[DepartmentResponse]


class BatchYearResponse(CamelBaseModel):
    id: int
    year: int


class BatchYearList(CamelBaseModel):
    count: int
    results: List[BatchYearResponse]


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
    views: int = Field(default_factory=lambda: random.randint(0, 500))


class ProjectList(CamelBaseModel):
    count: int
    results: List[ProjectResponse]


class ResponseOut(CamelBaseModel):
    message: str


class DiscussionIn(CamelBaseModel):
    comment: str = Field(..., max_length=5000)
    parent_id: Optional[int] = Field(None, description="ID of parent comment")


class LevelEnum(str, Enum):
    Masters = "Masters"
    Bachelors = "Bachelors"
    PHD = "PHD"


class TeamMemberPayload(CamelBaseModel):
    full_name: str
    roll_no: str
    photo: Optional[HttpUrl]


class ProjectFilePayload(CamelBaseModel):
    file_type: str
    file: HttpUrl


class SubmitProjectPayload(CamelBaseModel):
    title: str
    abstract: str
    batch_year: int
    category: int
    department: int
    level: LevelEnum
    supervisor: Optional[str]
    project_details: str
    technologies_used: str
    github_link: HttpUrl
    documentation_link: HttpUrl
    team_members: List[TeamMemberPayload]
    files: List[ProjectFilePayload]


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
    views: int = Field(default_factory=lambda: random.randint(0, 500))
    team_members: List[ProjectTeamMemberOut]
    files: List[ProjectFileOut]


class RateProjectPayload(CamelBaseModel):
    rating: int
