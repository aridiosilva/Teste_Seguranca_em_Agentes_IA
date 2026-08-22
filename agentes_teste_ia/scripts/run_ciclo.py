#!/usr/bin/env python3
"""
Ponto de entrada do ciclo de teste. Uso:

    python scripts/run_ciclo.py \
        --casos data/casos_teste_exemplo.json \
        --saida output/

Executa a bateria completa (20 casos por padrao), grava a evidencia em
JSONL e imprime o resumo do relatorio final no console.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# Garante que 'src/' esta no path quando o script e chamado da raiz do projeto
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from orquestrador import executar_ciclo  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa o ciclo de teste dos 3 agentes.")
    parser.add_argument("--casos", default=os.path.join(RAIZ, "data", "casos_teste_exemplo.json"),
                         help="Caminho para o JSON com a bateria de casos de teste.")
    parser.add_argument("--saida", default=os.path.join(RAIZ, "output"),
                         help="Diretorio onde a evidencia e o relatorio final serao gravados.")
    args = parser.parse_args()

    relatorio = executar_ciclo(args.casos, args.saida)

    print("=" * 60)
    print("CICLO DE TESTE CONCLUIDO")
    print("=" * 60)
    print(f"Total de casos executados : {relatorio['total_casos_executados']}")
    print(f"Distribuicao por camada    : {relatorio['distribuicao_por_camada']}")
    print(f"Distribuicao por veredito  : {relatorio['distribuicao_por_veredito']}")
    print(f"Distribuicao por severidade: {relatorio['distribuicao_por_severidade']}")
    print(f"Bloqueia release?          : {relatorio['bloqueio_de_release']}")
    print("-" * 60)
    if relatorio["achados_pendentes_revisao_humana"]:
        print("Achados pendentes de revisao humana (Critica/Alta):")
        for achado in relatorio["achados_pendentes_revisao_humana"]:
            print(f"  - [{achado['severidade']}] {achado['id_caso']}: {achado['justificativa']}")
    else:
        print("Nenhum achado Critico/Alto pendente de revisao humana.")
    print("=" * 60)
    print(f"Evidencia completa em: {args.saida}")
    print(f"  - casos_registrados.jsonl")
    print(f"  - execucoes.jsonl")
    print(f"  - vereditos.jsonl")
    print(f"  - relatorio_final.json")

    return 1 if relatorio["bloqueio_de_release"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
