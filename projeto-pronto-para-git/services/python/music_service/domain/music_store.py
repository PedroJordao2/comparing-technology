from music_service.application.catalog_service import (
    CatalogDomainError,
    CatalogService,
    plain_error,
)

DomainError = CatalogDomainError
MusicStore = CatalogService

__all__ = ["CatalogDomainError", "CatalogService", "DomainError", "MusicStore", "plain_error"]
