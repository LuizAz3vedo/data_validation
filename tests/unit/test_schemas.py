"""Testes unitários para schemas de domínio."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from extractor.schemas.domains.contact import Empresa, Pessoa
from extractor.schemas.domains.ecommerce import Produto, Review
from extractor.schemas.domains.financial import Fatura, Transacao
from extractor.schemas.domains.legal import Contrato
from extractor.schemas.domains.medical import Diagnostico, Prescricao


class TestDiagnostico:
    """Testes para schema Diagnostico."""

    def test_valid_diagnostico(self) -> None:
        """Cria diagnóstico válido."""
        diag = Diagnostico(
            condicao="Síndrome gripal",
            gravidade="moderada",
            sintomas=["febre", "tosse"],
            recomendacoes=["repouso", "hidratação"],
        )
        assert diag.condicao == "Síndrome gripal"
        assert diag.gravidade == "moderada"
        assert len(diag.sintomas) == 2
        assert diag.urgencia is False

    def test_invalid_gravidade(self) -> None:
        """Gravidade inválida deve falhar."""
        with pytest.raises(ValidationError) as exc_info:
            Diagnostico(
                condicao="Teste",
                gravidade="critica",  # type: ignore[arg-type]
                sintomas=["febre"],
                recomendacoes=["repouso"],
            )
        assert "gravidade" in str(exc_info.value)

    def test_empty_sintomas_fails(self) -> None:
        """Lista vazia de sintomas deve falhar."""
        with pytest.raises(ValidationError):
            Diagnostico(
                condicao="Teste",
                gravidade="leve",
                sintomas=[],
                recomendacoes=["repouso"],
            )

    def test_urgencia_true(self) -> None:
        """Diagnóstico com urgência."""
        diag = Diagnostico(
            condicao="Infarto",
            gravidade="grave",
            sintomas=["dor no peito", "falta de ar"],
            recomendacoes=["emergência imediata"],
            urgencia=True,
        )
        assert diag.urgencia is True


class TestPrescricao:
    """Testes para schema Prescricao."""

    def test_valid_prescricao(self) -> None:
        """Cria prescrição válida."""
        presc = Prescricao(
            medicamento="Paracetamol",
            dosagem="750mg",
            frequencia="6/6h",
            duracao="5 dias",
            via_administracao="oral",
        )
        assert presc.medicamento == "Paracetamol"
        assert presc.observacoes is None

    def test_with_observacoes(self) -> None:
        """Prescrição com observações."""
        presc = Prescricao(
            medicamento="Amoxicilina",
            dosagem="500mg",
            frequencia="8/8h",
            duracao="7 dias",
            via_administracao="oral",
            observacoes="Tomar após as refeições",
        )
        assert presc.observacoes == "Tomar após as refeições"


class TestFatura:
    """Testes para schema Fatura."""

    def test_valid_fatura(self) -> None:
        """Cria fatura válida."""
        fatura = Fatura(
            numero_fatura="2024-001",
            emitente="Empresa A",
            destinatario="Cliente B",
            data_emissao=date(2024, 1, 15),
            data_vencimento=date(2024, 2, 15),
            valor_total=Decimal("1500.00"),
            itens=["Serviço de consultoria"],
        )
        assert fatura.valor_total == Decimal("1500.00")
        assert fatura.moeda == "BRL"

    def test_valor_negativo_fails(self) -> None:
        """Valor negativo deve falhar."""
        with pytest.raises(ValidationError):
            Fatura(
                numero_fatura="2024-001",
                emitente="Empresa A",
                destinatario="Cliente B",
                data_emissao=date(2024, 1, 15),
                data_vencimento=date(2024, 2, 15),
                valor_total=Decimal("-100.00"),
                itens=["Item"],
            )


class TestTransacao:
    """Testes para schema Transacao."""

    def test_valid_transacao_pix(self) -> None:
        """Cria transação PIX válida."""
        trans = Transacao(
            tipo="pix",
            valor=Decimal("250.00"),
            data=date(2024, 1, 20),
            descricao="Pagamento aluguel",
        )
        assert trans.tipo == "pix"
        assert trans.categoria is None

    def test_transacao_with_categoria(self) -> None:
        """Transação com categoria."""
        trans = Transacao(
            tipo="debito",
            valor=Decimal("50.00"),
            data=date(2024, 1, 21),
            descricao="Supermercado",
            categoria="alimentação",
        )
        assert trans.categoria == "alimentação"


class TestContrato:
    """Testes para schema Contrato."""

    def test_valid_contrato(self) -> None:
        """Cria contrato válido."""
        contrato = Contrato(
            tipo_contrato="Prestação de Serviços",
            partes=["Empresa A", "Empresa B"],
            objeto="Desenvolvimento de software",
            clausulas_principais=["Prazo de entrega", "Valor mensal"],
        )
        assert len(contrato.partes) == 2
        assert contrato.valor is None

    def test_contrato_menos_de_duas_partes_fails(self) -> None:
        """Contrato precisa de pelo menos 2 partes."""
        with pytest.raises(ValidationError):
            Contrato(
                tipo_contrato="Teste",
                partes=["Só uma parte"],
                objeto="Objeto",
                clausulas_principais=["Cláusula"],
            )

    def test_contrato_completo(self) -> None:
        """Contrato com todos os campos."""
        contrato = Contrato(
            tipo_contrato="Aluguel",
            partes=["Locador", "Locatário"],
            objeto="Imóvel residencial",
            valor="R$ 2.000,00/mês",
            vigencia_inicio=date(2024, 1, 1),
            vigencia_fim=date(2025, 1, 1),
            clausulas_principais=["Prazo", "Valor", "Multa"],
            penalidades=["Multa de 10% por atraso"],
        )
        assert contrato.valor == "R$ 2.000,00/mês"
        assert len(contrato.penalidades) == 1


class TestProduto:
    """Testes para schema Produto."""

    def test_valid_produto(self) -> None:
        """Cria produto válido."""
        produto = Produto(
            nome="Smartphone XYZ",
            descricao="Celular última geração",
            preco=Decimal("2999.99"),
            categoria="Eletrônicos",
        )
        assert produto.disponivel is True
        assert produto.especificacoes == {}

    def test_produto_com_especificacoes(self) -> None:
        """Produto com especificações técnicas."""
        produto = Produto(
            nome="Notebook ABC",
            descricao="Notebook para trabalho",
            preco=Decimal("4500.00"),
            categoria="Informática",
            marca="Dell",
            especificacoes={
                "RAM": "16GB",
                "SSD": "512GB",
                "Processador": "Intel i7",
            },
        )
        assert produto.marca == "Dell"
        assert produto.especificacoes["RAM"] == "16GB"


class TestReview:
    """Testes para schema Review."""

    def test_valid_review_positivo(self) -> None:
        """Cria review positivo válido."""
        review = Review(
            produto="Fone de Ouvido XYZ",
            nota=5,
            sentimento="positivo",
            pontos_positivos=["Qualidade de som", "Confortável"],
            recomenda=True,
        )
        assert review.nota == 5
        assert review.sentimento == "positivo"

    def test_review_negativo(self) -> None:
        """Cria review negativo."""
        review = Review(
            produto="Produto Ruim",
            nota=1,
            sentimento="negativo",
            pontos_negativos=["Quebrou rápido", "Atendimento ruim"],
            recomenda=False,
        )
        assert review.nota == 1
        assert not review.recomenda

    def test_nota_fora_do_range_fails(self) -> None:
        """Nota fora do range 1-5 deve falhar."""
        with pytest.raises(ValidationError):
            Review(
                produto="Produto",
                nota=6,
                sentimento="positivo",
                recomenda=True,
            )

        with pytest.raises(ValidationError):
            Review(
                produto="Produto",
                nota=0,
                sentimento="negativo",
                recomenda=False,
            )


class TestPessoa:
    """Testes para schema Pessoa."""

    def test_valid_pessoa(self) -> None:
        """Cria pessoa válida."""
        pessoa = Pessoa(
            nome_completo="Maria Santos",
            email="maria@example.com",
            telefone="(11) 99999-8888",
        )
        assert pessoa.nome_completo == "Maria Santos"
        assert pessoa.telefone == "11999998888"

    def test_telefone_normalization(self) -> None:
        """Telefone deve ser normalizado."""
        pessoa = Pessoa(
            nome_completo="João",
            telefone="+55 (11) 9.9999-8888",
        )
        assert pessoa.telefone == "+5511999998888"

    def test_invalid_email_fails(self) -> None:
        """Email inválido deve falhar."""
        with pytest.raises(ValidationError):
            Pessoa(
                nome_completo="Teste",
                email="nao_eh_email",
            )

    def test_pessoa_completa(self) -> None:
        """Pessoa com todos os campos."""
        pessoa = Pessoa(
            nome_completo="Carlos Silva",
            email="carlos@empresa.com",
            telefone="11987654321",
            cargo="Gerente de TI",
            empresa="Tech Corp",
            linkedin="linkedin.com/in/carlossilva",
        )
        assert pessoa.cargo == "Gerente de TI"


class TestEmpresa:
    """Testes para schema Empresa."""

    def test_valid_empresa(self) -> None:
        """Cria empresa válida."""
        empresa = Empresa(
            razao_social="Tech Solutions Ltda",
        )
        assert empresa.razao_social == "Tech Solutions Ltda"
        assert empresa.nome_fantasia is None

    def test_empresa_completa(self) -> None:
        """Empresa com todos os campos."""
        empresa = Empresa(
            razao_social="Empresa ABC Ltda",
            nome_fantasia="ABC Tech",
            cnpj="12.345.678/0001-90",
            endereco="Av. Paulista, 1000",
            setor="Tecnologia",
            contato_principal="João Silva",
        )
        assert empresa.nome_fantasia == "ABC Tech"
        assert empresa.setor == "Tecnologia"
