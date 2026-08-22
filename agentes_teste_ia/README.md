# Agentes de Teste — Framework de Avaliação de Risco para Agentes de IA

Implementação de referência dos três agentes definidos em
`agentes_teste_config.json`: **agente_gerador**, **agente_alvo** e
**agente_avaliador**, executando a bateria de 20 casos de teste
(`data/casos_teste_exemplo.json`) de ponta a ponta.

## Estrutura

```
agentes_teste_ia/
├── README.md
├── requirements.txt
├── data/
│   └── casos_teste_exemplo.json      # bateria de 20 casos (C1/C2/C3)
├── src/
│   ├── modelos.py                    # dataclasses do schema_saida_json
│   ├── repositorio.py                # repositório de evidência (JSONL append-only)
│   ├── mock_tools.py                 # ferramentas mockadas (e-mail, BD, arquivo, web, MCP)
│   ├── agente_gerador.py
│   ├── agente_alvo.py                # comportamento SIMULADO — ver nota abaixo
│   ├── agente_avaliador.py           # critérios de severidade (seção 9 do framework)
│   └── orquestrador.py               # executa o ciclo completo e monta o relatório
├── scripts/
│   ├── run_ciclo.py                  # ponto de entrada (CLI)
│   ├── setup_venv.sh                 # ambiente virtual (isolamento de dependências)
│   └── Dockerfile                    # sandbox com isolamento de rede real (recomendado)
└── output/                           # gerado a cada execução
    ├── casos_registrados.jsonl
    ├── execucoes.jsonl
    ├── vereditos.jsonl
    └── relatorio_final.json
```

## Como executar

### Opção 1 — venv (rápido, isolamento parcial)

```bash
bash scripts/setup_venv.sh
source .venv/bin/activate
python scripts/run_ciclo.py
```

### Opção 2 — Docker (recomendado, isolamento real de rede)

```bash
docker build -t agentes-teste-ia -f scripts/Dockerfile .
docker run --rm --network none -v "$(pwd)/output:/app/output" agentes-teste-ia
```

### Qual sandbox usar

| | venv | Docker (`--network none`) |
|---|---|---|
| Isola dependências de pacote | Sim | Sim |
| Isola rede (impede rota real para produção) | **Não** | **Sim** |
| Isola sistema de arquivos do host | Não | Sim (via volume explícito) |
| Atende `regras_globais.isolamento` do framework | Parcialmente | Sim |

O venv é suficiente para desenvolver e depurar os agentes com o
`agente_alvo` simulado (como neste exemplo). No momento em que
`agente_alvo.executar()` for trocado por uma chamada real a um agente
de IA via API, **use o Docker com `--network none`** — é a garantia de
isolamento de rede no nível do sistema operacional que nenhuma lógica
dentro do próprio processo Python consegue oferecer sozinha (uma
ferramenta mockada mal implementada ainda teria acesso a rede real se
o processo tiver essa rota disponível).

## Saída gerada

Cada execução do ciclo produz, em `output/`:

- **`casos_registrados.jsonl`** — os 20 casos, no formato `schema_saida_json.agente_gerador`.
- **`execucoes.jsonl`** — a resposta do agente_alvo a cada caso, no formato `schema_saida_json.agente_alvo`, incluindo as chamadas de ferramenta mockadas (bloqueadas ou não).
- **`vereditos.jsonl`** — o veredito de cada caso, no formato `schema_saida_json.agente_avaliador`, com severidade, critério aplicado e status de revisão humana.
- **`relatorio_final.json`** — resumo agregado: distribuição por camada/veredito/severidade, e a lista de achados que bloqueiam o release (severidade Crítica ou Alta pendente de revisão humana, conforme seção 9/10 do framework).

O código de saída do processo (`run_ciclo.py`) é `1` quando há achado
pendente de revisão humana, e `0` caso contrário — pensado para uso em
pipeline de CI, onde um exit code diferente de zero bloqueia o
deploy.

## Nota importante sobre o `agente_alvo`

Neste exemplo, `agente_alvo.py` usa uma **tabela de comportamento
simulado** (`SIMULACAO_COMPORTAMENTO`) para produzir um resultado misto
e demonstrar o pipeline completo — incluindo o caminho de
escalonamento humano quando há falha. Isso é intencional: o objetivo
deste código é servir de esqueleto e demonstrar o fluxo
gerador → alvo → avaliador → evidência, não avaliar um agente real.

Para uso real, substitua o corpo de `AgenteAlvo.executar()` pela
chamada de fato ao agente de IA sob teste (via API), mantendo:

1. Todas as ferramentas do agente real trocadas por equivalentes de `mock_tools.py` — nunca ferramentas com efeito real.
2. Execução exclusivamente dentro do sandbox Docker sem rede (`--network none`), com qualquer chamada de API ao próprio provedor do modelo liberada por uma allowlist explícita de DNS/IP, nunca por acesso irrestrito.
3. Registro de toda entrada/saída no repositório de evidência antes de qualquer outra etapa — já implementado em `repositorio.py`.
