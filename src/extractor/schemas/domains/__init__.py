"""Domain schemas - Schemas específicos por domínio."""

from extractor.schemas.domains.contact import Empresa, Pessoa
from extractor.schemas.domains.ecommerce import Produto, Review
from extractor.schemas.domains.financial import Fatura, Transacao
from extractor.schemas.domains.legal import Contrato
from extractor.schemas.domains.medical import Diagnostico, Prescricao

__all__ = [
    "Contrato",
    "Diagnostico",
    "Empresa",
    "Fatura",
    "Pessoa",
    "Prescricao",
    "Produto",
    "Review",
    "Transacao",
]
