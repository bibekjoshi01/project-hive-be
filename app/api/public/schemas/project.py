from pydantic import Field
from typing import List, Optional

from app.utils.casing import CamelBaseModel


class CategoryResponse(CamelBaseModel):
    id: int
    name: str


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


class ProjectResponse(CamelBaseModel):
    id: int
    title: str
    abstract: str
    level: str
    supervisor: str
    technologies_used: str
    github_link: Optional[str]
    documentation_link: Optional[str]
    status: str
    submitted_at: str
    category_id: int
    department_id: int
    batch_year_id: int
    rating_average: float = Field(..., example=4.2)


class ProjectList(CamelBaseModel):
    count: int
    results: List[ProjectResponse]
