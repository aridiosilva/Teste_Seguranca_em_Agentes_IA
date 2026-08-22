# Sandbox recomendado para o ciclo de teste dos 3 agentes.
#
# Por que Docker em vez de venv: o venv isola apenas pacotes Python — o
# processo ainda tem acesso irrestrito a rede e sistema de arquivos do
# host. O framework exige (secao 3, escopo_execucao) um ambiente sem
# rota de rede para sistemas reais. `docker run --network none` garante
# isso no nivel do SO, o que nenhuma configuracao dentro do proprio
# processo Python consegue garantir sozinha (uma ferramenta mockada
# pode ser mal implementada; a ausencia de interface de rede, nao).
#
# Build:
#   docker build -t agentes-teste-ia -f scripts/Dockerfile .
#
# Run (sandbox real, sem rede):
#   docker run --rm --network none \
#     -v "$(pwd)/output:/app/output" \
#     agentes-teste-ia

FROM python:3.12-slim

# Usuario nao-root — nenhum dos 3 agentes precisa de privilegio elevado
RUN useradd --create-home --uid 1000 sandboxuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

COPY src/ ./src/
COPY scripts/run_ciclo.py ./scripts/run_ciclo.py
COPY data/ ./data/

RUN mkdir -p /app/output && chown -R sandboxuser:sandboxuser /app
USER sandboxuser

ENTRYPOINT ["python", "scripts/run_ciclo.py"]
