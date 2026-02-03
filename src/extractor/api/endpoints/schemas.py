"""Endpoint para listar schemas disponíveis."""

from typing import Annotated

from fastapi import APIRouter, Depends

from extractor.core.extractor import ExtractorService
from extractor.dependencies import get_extractor
from extractor.schemas.requests import SchemaListResponse

router = APIRouter(tags=["schemas"])


@router.get(
    "/schemas",
    response_model=SchemaListResponse,
    summary="Lista schemas disponíveis",
    description="Retorna todos os schemas de extração registrados com seus metadados.",
)
async def list_schemas(
    extractor: Annotated[ExtractorService, Depends(get_extractor)],
) -> SchemaListResponse:
    """Lista todos os schemas disponíveis."""
    schemas = extractor.list_schemas()
    return SchemaListResponse(
        schemas=schemas,
        total=len(schemas),
    )
