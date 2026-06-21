from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class Params(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)

def paginate(query, params: Params, schema: T) -> Page[T]:
    total = query.count()
    items = query.offset((params.page - 1) * params.size).limit(params.size).all()
    pages = (total + params.size - 1) // params.size
    
    return Page(
        items=[schema.from_orm(item) for item in items],
        total=total,
        page=params.page,
        size=params.size,
        pages=pages
    )
