"""Endpoint principal de extração."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from extractor.core.extractor import ExtractionError, ExtractorService
from extractor.dependencies import get_extractor
from extractor.schemas.requests import (
    ErrorResponse,
    ExtractionRequest,
    ExtractionResponse,
)
from extractor.utils.logging import get_logger

router = APIRouter(tags=["extraction"])
logger = get_logger(__name__)


@router.post(
    "/extract",
    response_model=ExtractionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Schema não encontrado"},
        422: {"model": ErrorResponse, "description": "Validação falhou"},
        500: {"model": ErrorResponse, "description": "Erro de extração"},
    },
    summary="Extrai dados estruturados de texto",
    description="""
    Recebe texto não estruturado e extrai dados conforme o schema especificado.

    O sistema usa LLMs (Ollama local ou APIs cloud) com validação Pydantic
    para garantir outputs tipados. Retry automático em caso de falha.
    """,
)
async def extract_data(
    request: ExtractionRequest,
    extractor: Annotated[ExtractorService, Depends(get_extractor)],
) -> ExtractionResponse:
    """Extrai dados estruturados do texto."""
    try:
        result = await extractor.extract(
            text=request.text,
            schema_name=request.schema_name,
            system_prompt=request.system_prompt,
            use_cache=request.use_cache,
        )
        return ExtractionResponse(
            success=True,
            schema_name=request.schema_name,
            data=result,
        )

    except KeyError as e:
        logger.warning("schema_not_found", schema=request.schema_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    except ExtractionError as e:
        logger.error("extraction_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na extração: {e}",
        ) from e
