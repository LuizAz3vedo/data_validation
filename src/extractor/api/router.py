"""Router principal da API."""

from fastapi import APIRouter

from extractor.api.endpoints import extract, health, schemas

api_router = APIRouter()

api_router.include_router(extract.router)
api_router.include_router(schemas.router)
api_router.include_router(health.router)
