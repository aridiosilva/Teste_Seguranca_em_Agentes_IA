"""
Repositorio de evidencia: armazenamento append-only (JSONL) compartilhado
pelos tres agentes. Nenhum agente mantem memoria propria entre casos alem
deste repositorio (regra 'nunca_lembrar' do framework).
"""

from __future__ import annotations

import json
import os
from typing import Iterable


class RepositorioEvidencia:
    def __init__(self, diretorio_saida: str):
        os.makedirs(diretorio_saida, exist_ok=True)
        self.caminho_casos = os.path.join(diretorio_saida, "casos_registrados.jsonl")
        self.caminho_execucoes = os.path.join(diretorio_saida, "execucoes.jsonl")
        self.caminho_vereditos = os.path.join(diretorio_saida, "vereditos.jsonl")
        # Trunca os arquivos no inicio de cada ciclo de execucao (novo lote de evidencia)
        for caminho in (self.caminho_casos, self.caminho_execucoes, self.caminho_vereditos):
            open(caminho, "w", encoding="utf-8").close()

    @staticmethod
    def _append(caminho: str, registro: dict) -> None:
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    def registrar_caso(self, caso: dict) -> None:
        self._append(self.caminho_casos, caso)

    def registrar_execucao(self, execucao: dict) -> None:
        self._append(self.caminho_execucoes, execucao)

    def registrar_veredito(self, veredito: dict) -> None:
        self._append(self.caminho_vereditos, veredito)

    @staticmethod
    def _ler_jsonl(caminho: str) -> Iterable[dict]:
        if not os.path.exists(caminho):
            return []
        with open(caminho, "r", encoding="utf-8") as f:
            return [json.loads(linha) for linha in f if linha.strip()]

    def ler_casos(self) -> list:
        return list(self._ler_jsonl(self.caminho_casos))

    def ler_execucoes(self) -> list:
        return list(self._ler_jsonl(self.caminho_execucoes))

    def ler_vereditos(self) -> list:
        return list(self._ler_jsonl(self.caminho_vereditos))
