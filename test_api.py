"""Script simples para testar a API."""

import httpx

API_URL = "http://127.0.0.1:8001"


def extrair(texto: str, schema: str) -> dict:
    """Envia texto para API e retorna dados estruturados."""
    response = httpx.post(
        f"{API_URL}/api/v1/extract",
        json={"text": texto, "schema_name": schema},
        timeout=120.0,  # LLM pode demorar (2 min)
    )
    return response.json()


if __name__ == "__main__":
    # Exemplo 1: Extrair dados de pessoa
    texto_pessoa = """
    Conheci Maria Santos na conferência de IA.
    Ela é Diretora de Tecnologia na StartupXYZ.
    Email: maria.santos@startupxyz.com
    Telefone: (11) 98765-4321
    LinkedIn: linkedin.com/in/mariasantos
    """

    print("=" * 50)
    print("EXTRAINDO PESSOA:")
    print("=" * 50)
    resultado = extrair(texto_pessoa, "Pessoa")
    print(f"Sucesso: {resultado['success']}")
    print(f"Dados: {resultado['data']}")

    # Exemplo 2: Extrair diagnóstico médico
    texto_medico = """
    Paciente apresenta febre alta de 39°C há 3 dias,
    dor de cabeça intensa, tosse seca e fadiga.
    Diagnóstico: Síndrome gripal.
    Gravidade: moderada.
    Recomendações: repouso absoluto, hidratação,
    paracetamol 750mg a cada 6 horas se febre.
    """

    print("\n" + "=" * 50)
    print("EXTRAINDO DIAGNÓSTICO:")
    print("=" * 50)
    resultado = extrair(texto_medico, "Diagnostico")
    print(f"Sucesso: {resultado['success']}")
    print(f"Dados: {resultado['data']}")

    # Exemplo 3: Extrair review de produto
    texto_review = """
    Comprei o iPhone 15 Pro e estou muito satisfeito!
    A câmera é incrível, bateria dura o dia todo.
    Único ponto negativo é o preço alto.
    Nota: 4 de 5 estrelas. Recomendo a compra!
    """

    print("\n" + "=" * 50)
    print("EXTRAINDO REVIEW:")
    print("=" * 50)
    resultado = extrair(texto_review, "Review")
    print(f"Sucesso: {resultado['success']}")
    print(f"Dados: {resultado['data']}")
