#!/usr/bin/env bash
# Cria e prepara um ambiente virtual Python para rodar o ciclo de teste.
#
# IMPORTANTE: um venv isola apenas DEPENDENCIAS de pacote — ele NAO
# fornece isolamento de rede, sistema de arquivos ou processo. Para o
# escopo_execucao exigido pelo framework (sandbox real, sem rota de
# rede para producao), use scripts/Dockerfile em vez deste script
# sempre que o ciclo envolver uma chamada real ao agente_alvo (ver
# README.md, secao "Qual sandbox usar").
#
# Uso:
#   bash scripts/setup_venv.sh
#   source .venv/bin/activate
#   python scripts/run_ciclo.py

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

echo "Criando ambiente virtual em .venv ..."
python3 -m venv .venv

echo "Ativando e instalando dependencias (somente biblioteca padrao neste exemplo)..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
if [ -s requirements.txt ]; then
  pip install -r requirements.txt --quiet
fi

echo ""
echo "Ambiente pronto. Para executar a bateria de testes:"
echo "  source .venv/bin/activate"
echo "  python scripts/run_ciclo.py"
