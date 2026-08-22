#!/usr/bin/env python3
"""
Ponto de entrada do ciclo de teste. Uso:

    python scripts/run_ciclo.py \
        --config config/agentes_teste_config.json \
        --casos data/casos_teste_exemplo.json \
        --saida output/

Carrega e valida o agentes_teste_config.json (guardrails, criterios de
severidade, allowlist de sandbox), executa a bateria completa e grava
a evidencia em JSONL.
"""

from __future__ import annotations

import argparse
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from orquestrador import executar_ciclo  # noqa: E402
from config_loader import ConfigInvalidaError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa o ciclo de teste dos 3 agentes.")
    parser.add_argument("--config", default=os.path.join(RAIZ, "config", "agentes_teste_config.json"),
                         help="Caminho para o agentes_teste_config.json.")
    parser.add_argument("--casos", default=os.path.join(RAIZ, "data", "casos_teste_exemplo.json"),
                         help="Caminho para o JSON com a bateria de casos de teste.")
    parser.add_argument("--saida", default=os.path.join(RAIZ, "output"),
                         help="Diretorio onde a evidencia e o relatorio final serao gravados.")
    args = parser.parse_args()

    try:
        relatorio = executar_ciclo(args.casos, args.saida, args.config)
    except ConfigInvalidaError as exc:
        print(f"ERRO: config invalido — {exc}", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError) as exc:
        print(f"ERRO: ciclo abortado por guardrail — {exc}", file=sys.stderr)
        return 2

    print("=" * 60)
    print("CICLO DE TESTE CONCLUIDO")
    print("=" * 60)
    print(f"Config utilizado           : {relatorio['config_utilizado']}")
    print(f"Total de casos executados  : {relatorio['total_casos_executados']}")
    print(f"Distribuicao por camada    : {relatorio['distribuicao_por_camada']}")
    print(f"Distribuicao por veredito  : {relatorio['distribuicao_por_veredito']}")
    print(f"Distribuicao por severidade: {relatorio['distribuicao_por_severidade']}")
    print(f"Bloqueia release?          : {relatorio['bloqueio_de_release']}")
    print("-" * 60)
    if relatorio["achados_pendentes_revisao_humana"]:
        print("Achados pendentes de revisao humana (conforme config.regras_globais):")
        for achado in relatorio["achados_pendentes_revisao_humana"]:
            print(f"  - [{achado['severidade']}] {achado['id_caso']}: {achado['justificativa']}")
    else:
        print("Nenhum achado pendente de revisao humana.")
    if relatorio["casos_com_conflito_de_interesse_sinalizado"]:
        print("-" * 60)
        print(f"Conflito de interesse sinalizado em: "
              f"{relatorio['casos_com_conflito_de_interesse_sinalizado']}")
    print("=" * 60)
    print(f"Evidencia completa em: {args.saida}")
    print("  - casos_registrados.jsonl")
    print("  - execucoes.jsonl")
    print("  - vereditos.jsonl")
    print("  - relatorio_final.json")

    return 1 if relatorio["bloqueio_de_release"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
