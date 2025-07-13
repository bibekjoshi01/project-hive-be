from pydantic import BaseModel, Field
from typing import List


class CategoryResponse(BaseModel):
    id: int
    name: str


class CategoryList(BaseModel):
    count: int
    results: List[CategoryResponse]


class DepartmentResponse(BaseModel):
    id: int
    name: str


class DepartmentList(BaseModel):
    count: int
    results: List[DepartmentResponse]


class BatchYearResponse(BaseModel):
    id: int
    year: int


class BatchYearList(BaseModel):
    count: int
    results: List[BatchYearResponse]
