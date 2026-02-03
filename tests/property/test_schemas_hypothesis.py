"""Testes baseados em propriedades com Hypothesis.

Property-based testing testa PROPRIEDADES que devem ser verdadeiras
para QUALQUER input válido, não apenas casos específicos.

Exemplo de propriedades testadas:
- Serialização/deserialização (roundtrip) sempre preserva dados
- Campos obrigatórios sempre estão presentes
- Validadores sempre produzem output consistente
- Constraints (ge=0, le=5) são sempre respeitadas
"""

from datetime import date
from decimal import Decimal
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from extractor.schemas.domains.contact import Empresa, Pessoa
from extractor.schemas.domains.ecommerce import Produto, Review
from extractor.schemas.domains.financial import Fatura, Transacao
from extractor.schemas.domains.legal import Contrato
from extractor.schemas.domains.medical import Diagnostico, Prescricao

# ============================================================
# ESTRATÉGIAS CUSTOMIZADAS (Custom Strategies)
# ============================================================

# Estratégia para gerar strings não vazias (usando alphabet para evitar filtro lento)
non_empty_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=1,
    max_size=50,
)

# Estratégia para gerar emails válidos (simplificado para performance)
valid_emails = st.from_regex(r"[a-z]{3,10}@[a-z]{3,10}\.(com|org|net)", fullmatch=True)

# Estratégia para gerar telefones brasileiros
telefones = st.from_regex(r"\(\d{2}\) \d{4,5}-\d{4}", fullmatch=True)

# Estratégia para gerar datas razoáveis
reasonable_dates = st.dates(
    min_value=date(2000, 1, 1),
    max_value=date(2030, 12, 31),
)

# Estratégia para gerar valores monetários positivos
positive_decimals = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("1000000.00"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)


# ============================================================
# ESTRATÉGIAS COMPOSTAS (Composite Strategies)
# ============================================================


@st.composite
def pessoa_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Pessoa."""
    return {
        "nome_completo": draw(non_empty_text),
        "email": draw(st.none() | valid_emails),
        "telefone": draw(st.none() | telefones),
        "cargo": draw(st.none() | non_empty_text),
        "empresa": draw(st.none() | non_empty_text),
        "linkedin": draw(st.none() | st.just("https://linkedin.com/in/user")),
    }


@st.composite
def empresa_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Empresa."""
    return {
        "razao_social": draw(non_empty_text),
        "nome_fantasia": draw(st.none() | non_empty_text),
        "cnpj": draw(st.none() | st.from_regex(r"\d{14}", fullmatch=True)),
        "endereco": draw(st.none() | non_empty_text),
        "setor": draw(st.none() | non_empty_text),
        "contato_principal": draw(st.none() | non_empty_text),
    }


@st.composite
def diagnostico_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Diagnostico."""
    return {
        "condicao": draw(non_empty_text),
        "gravidade": draw(st.sampled_from(["leve", "moderada", "grave"])),
        "sintomas": draw(st.lists(non_empty_text, min_size=1, max_size=5)),
        "recomendacoes": draw(st.lists(non_empty_text, min_size=1, max_size=5)),
        "urgencia": draw(st.booleans()),
    }


@st.composite
def prescricao_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Prescricao."""
    return {
        "medicamento": draw(non_empty_text),
        "dosagem": draw(st.from_regex(r"\d+mg", fullmatch=True)),
        "frequencia": draw(st.from_regex(r"\d+/\d+h", fullmatch=True)),
        "duracao": draw(non_empty_text),
        "via_administracao": draw(
            st.sampled_from(["oral", "intravenosa", "topica", "outra"])
        ),
        "observacoes": draw(st.none() | non_empty_text),
    }


@st.composite
def produto_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Produto."""
    return {
        "nome": draw(non_empty_text),
        "descricao": draw(non_empty_text),
        "preco": draw(positive_decimals),
        "categoria": draw(non_empty_text),
        "marca": draw(st.none() | non_empty_text),
        "especificacoes": draw(st.dictionaries(non_empty_text, non_empty_text)),
        "disponivel": draw(st.booleans()),
    }


@st.composite
def review_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Review."""
    return {
        "produto": draw(non_empty_text),
        "nota": draw(st.integers(min_value=1, max_value=5)),
        "sentimento": draw(st.sampled_from(["positivo", "negativo", "neutro"])),
        "pontos_positivos": draw(st.lists(non_empty_text, max_size=5)),
        "pontos_negativos": draw(st.lists(non_empty_text, max_size=5)),
        "recomenda": draw(st.booleans()),
    }


@st.composite
def fatura_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Fatura."""
    data_emissao = draw(reasonable_dates)
    # Vencimento sempre após emissão
    data_vencimento = draw(
        st.dates(
            min_value=data_emissao,
            max_value=date(2030, 12, 31),
        )
    )
    return {
        "numero_fatura": draw(st.from_regex(r"\d{4}-\d{4}", fullmatch=True)),
        "emitente": draw(non_empty_text),
        "destinatario": draw(non_empty_text),
        "data_emissao": data_emissao,
        "data_vencimento": data_vencimento,
        "valor_total": draw(positive_decimals),
        "moeda": draw(st.sampled_from(["BRL", "USD", "EUR"])),
        "itens": draw(st.lists(non_empty_text, min_size=1, max_size=10)),
    }


@st.composite
def transacao_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Transacao."""
    return {
        "tipo": draw(st.sampled_from(["credito", "debito", "transferencia", "pix"])),
        "valor": draw(positive_decimals),
        "data": draw(reasonable_dates),
        "descricao": draw(non_empty_text),
        "categoria": draw(st.none() | non_empty_text),
        "origem": draw(st.none() | non_empty_text),
        "destino": draw(st.none() | non_empty_text),
    }


@st.composite
def contrato_strategy(draw: st.DrawFn) -> dict[str, Any]:
    """Gera dados válidos para schema Contrato."""
    vigencia_inicio = draw(st.none() | reasonable_dates)
    vigencia_fim = None
    if vigencia_inicio:
        vigencia_fim = draw(
            st.none()
            | st.dates(
                min_value=vigencia_inicio,
                max_value=date(2030, 12, 31),
            )
        )
    return {
        "tipo_contrato": draw(non_empty_text),
        "partes": draw(st.lists(non_empty_text, min_size=2, max_size=5)),
        "objeto": draw(non_empty_text),
        "valor": draw(st.none() | st.from_regex(r"R\$ \d+\.\d{3},\d{2}")),
        "vigencia_inicio": vigencia_inicio,
        "vigencia_fim": vigencia_fim,
        "clausulas_principais": draw(st.lists(non_empty_text, min_size=1, max_size=5)),
        "penalidades": draw(st.lists(non_empty_text, max_size=3)),
    }


# ============================================================
# TESTES DE PROPRIEDADE: ROUNDTRIP (Serialização)
# ============================================================


class TestSerializationRoundtrip:
    """Testa que serializar e deserializar preserva dados.

    Propriedade: Para qualquer input válido, model.model_dump_json()
    seguido de Model.model_validate_json() deve retornar dados equivalentes.
    """

    @given(pessoa_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_pessoa_roundtrip(self, data: dict[str, Any]) -> None:
        """Pessoa serializa e deserializa corretamente."""
        pessoa = Pessoa(**data)
        json_str = pessoa.model_dump_json()
        restored = Pessoa.model_validate_json(json_str)
        assert pessoa == restored

    @given(empresa_strategy())
    @settings(max_examples=50)
    def test_empresa_roundtrip(self, data: dict[str, Any]) -> None:
        """Empresa serializa e deserializa corretamente."""
        empresa = Empresa(**data)
        json_str = empresa.model_dump_json()
        restored = Empresa.model_validate_json(json_str)
        assert empresa == restored

    @given(diagnostico_strategy())
    @settings(max_examples=50)
    def test_diagnostico_roundtrip(self, data: dict[str, Any]) -> None:
        """Diagnostico serializa e deserializa corretamente."""
        diagnostico = Diagnostico(**data)
        json_str = diagnostico.model_dump_json()
        restored = Diagnostico.model_validate_json(json_str)
        assert diagnostico == restored

    @given(prescricao_strategy())
    @settings(max_examples=50)
    def test_prescricao_roundtrip(self, data: dict[str, Any]) -> None:
        """Prescricao serializa e deserializa corretamente."""
        prescricao = Prescricao(**data)
        json_str = prescricao.model_dump_json()
        restored = Prescricao.model_validate_json(json_str)
        assert prescricao == restored

    @given(produto_strategy())
    @settings(max_examples=50)
    def test_produto_roundtrip(self, data: dict[str, Any]) -> None:
        """Produto serializa e deserializa corretamente."""
        produto = Produto(**data)
        json_str = produto.model_dump_json()
        restored = Produto.model_validate_json(json_str)
        assert produto == restored

    @given(review_strategy())
    @settings(max_examples=50)
    def test_review_roundtrip(self, data: dict[str, Any]) -> None:
        """Review serializa e deserializa corretamente."""
        review = Review(**data)
        json_str = review.model_dump_json()
        restored = Review.model_validate_json(json_str)
        assert review == restored

    @given(fatura_strategy())
    @settings(max_examples=50)
    def test_fatura_roundtrip(self, data: dict[str, Any]) -> None:
        """Fatura serializa e deserializa corretamente."""
        fatura = Fatura(**data)
        json_str = fatura.model_dump_json()
        restored = Fatura.model_validate_json(json_str)
        assert fatura == restored

    @given(transacao_strategy())
    @settings(max_examples=50)
    def test_transacao_roundtrip(self, data: dict[str, Any]) -> None:
        """Transacao serializa e deserializa corretamente."""
        transacao = Transacao(**data)
        json_str = transacao.model_dump_json()
        restored = Transacao.model_validate_json(json_str)
        assert transacao == restored

    @given(contrato_strategy())
    @settings(max_examples=50)
    def test_contrato_roundtrip(self, data: dict[str, Any]) -> None:
        """Contrato serializa e deserializa corretamente."""
        contrato = Contrato(**data)
        json_str = contrato.model_dump_json()
        restored = Contrato.model_validate_json(json_str)
        assert contrato == restored


# ============================================================
# TESTES DE PROPRIEDADE: VALIDAÇÃO
# ============================================================


class TestValidationProperties:
    """Testa propriedades de validação dos schemas."""

    @given(st.integers(min_value=1, max_value=5))
    def test_review_nota_valid_range_always_accepted(self, nota: int) -> None:
        """Notas entre 1 e 5 são sempre aceitas."""
        review = Review(
            produto="Produto X",
            nota=nota,
            sentimento="positivo",
            recomenda=True,
        )
        assert review.nota == nota

    @given(st.integers().filter(lambda x: x < 1 or x > 5))
    @settings(max_examples=20)
    def test_review_nota_invalid_range_always_rejected(self, nota: int) -> None:
        """Notas fora de 1-5 são sempre rejeitadas."""
        try:
            Review(
                produto="Produto X",
                nota=nota,
                sentimento="positivo",
                recomenda=True,
            )
            assert False, f"Deveria rejeitar nota {nota}"
        except ValidationError:
            pass  # Esperado

    @given(st.decimals(min_value=Decimal("0"), allow_nan=False, allow_infinity=False))
    @settings(max_examples=50)
    def test_produto_preco_non_negative_accepted(self, preco: Decimal) -> None:
        """Preços não negativos são aceitos."""
        produto = Produto(
            nome="Produto",
            descricao="Descrição",
            preco=preco,
            categoria="Categoria",
        )
        assert produto.preco >= 0

    @given(
        st.decimals(
            max_value=Decimal("-0.01"),
            allow_nan=False,
            allow_infinity=False,
        )
    )
    @settings(max_examples=20)
    def test_produto_preco_negative_rejected(self, preco: Decimal) -> None:
        """Preços negativos são rejeitados."""
        try:
            Produto(
                nome="Produto",
                descricao="Descrição",
                preco=preco,
                categoria="Categoria",
            )
            assert False, f"Deveria rejeitar preço {preco}"
        except ValidationError:
            pass  # Esperado


# ============================================================
# TESTES DE PROPRIEDADE: VALIDADORES CUSTOMIZADOS
# ============================================================


class TestCustomValidators:
    """Testa validadores customizados dos schemas."""

    @given(telefones)
    def test_pessoa_telefone_cleaned_only_digits(self, telefone: str) -> None:
        """Telefone é limpo para conter apenas dígitos."""
        pessoa = Pessoa(
            nome_completo="João Silva",
            telefone=telefone,
        )
        # Após validação, telefone deve ter apenas dígitos e +
        assert pessoa.telefone is not None
        assert all(c.isdigit() or c == "+" for c in pessoa.telefone)

    @given(st.text())
    @settings(max_examples=50)
    def test_pessoa_telefone_none_or_cleaned(self, telefone: str) -> None:
        """Telefone é None ou contém apenas dígitos após limpeza."""
        pessoa = Pessoa(
            nome_completo="João Silva",
            telefone=telefone if telefone else None,
        )
        if pessoa.telefone is not None:
            assert all(c.isdigit() or c == "+" for c in pessoa.telefone)


# ============================================================
# TESTES DE PROPRIEDADE: CONSTRAINTS DE LISTA
# ============================================================


class TestListConstraints:
    """Testa constraints de listas (min_length, etc)."""

    @given(st.lists(non_empty_text, min_size=0, max_size=0))
    def test_diagnostico_empty_sintomas_rejected(self, sintomas: list[str]) -> None:
        """Diagnóstico sem sintomas é rejeitado (min_length=1)."""
        try:
            Diagnostico(
                condicao="Gripe",
                gravidade="leve",
                sintomas=sintomas,
                recomendacoes=["Repouso"],
            )
            assert False, "Deveria rejeitar lista vazia de sintomas"
        except ValidationError:
            pass

    @given(st.lists(non_empty_text, min_size=0, max_size=1))
    def test_contrato_insufficient_partes_rejected(self, partes: list[str]) -> None:
        """Contrato com menos de 2 partes é rejeitado (min_length=2)."""
        try:
            Contrato(
                tipo_contrato="Prestação de Serviços",
                partes=partes,
                objeto="Desenvolvimento de software",
                clausulas_principais=["Cláusula 1"],
            )
            assert False, "Deveria rejeitar menos de 2 partes"
        except ValidationError:
            pass

    @given(st.lists(non_empty_text, min_size=2, max_size=5))
    @settings(max_examples=30)
    def test_contrato_valid_partes_accepted(self, partes: list[str]) -> None:
        """Contrato com 2+ partes é aceito."""
        contrato = Contrato(
            tipo_contrato="Prestação de Serviços",
            partes=partes,
            objeto="Desenvolvimento de software",
            clausulas_principais=["Cláusula 1"],
        )
        assert len(contrato.partes) >= 2


# ============================================================
# TESTES DE PROPRIEDADE: LITERAL TYPES
# ============================================================


class TestLiteralTypes:
    """Testa que Literal types só aceitam valores definidos."""

    @given(st.sampled_from(["leve", "moderada", "grave"]))
    def test_diagnostico_valid_gravidade_accepted(self, gravidade: str) -> None:
        """Gravidades válidas são aceitas."""
        diagnostico = Diagnostico(
            condicao="Gripe",
            gravidade=gravidade,
            sintomas=["Febre"],
            recomendacoes=["Repouso"],
        )
        assert diagnostico.gravidade == gravidade

    @given(st.text().filter(lambda x: x not in ["leve", "moderada", "grave"]))
    @settings(max_examples=20)
    def test_diagnostico_invalid_gravidade_rejected(self, gravidade: str) -> None:
        """Gravidades inválidas são rejeitadas."""
        try:
            Diagnostico(
                condicao="Gripe",
                gravidade=gravidade,
                sintomas=["Febre"],
                recomendacoes=["Repouso"],
            )
            assert False, f"Deveria rejeitar gravidade '{gravidade}'"
        except ValidationError:
            pass

    @given(st.sampled_from(["positivo", "negativo", "neutro"]))
    def test_review_valid_sentimento_accepted(self, sentimento: str) -> None:
        """Sentimentos válidos são aceitos."""
        review = Review(
            produto="Produto X",
            nota=5,
            sentimento=sentimento,
            recomenda=True,
        )
        assert review.sentimento == sentimento

    @given(st.sampled_from(["credito", "debito", "transferencia", "pix"]))
    def test_transacao_valid_tipo_accepted(self, tipo: str) -> None:
        """Tipos de transação válidos são aceitos."""
        transacao = Transacao(
            tipo=tipo,
            valor=Decimal("100.00"),
            data=date.today(),
            descricao="Pagamento",
        )
        assert transacao.tipo == tipo
