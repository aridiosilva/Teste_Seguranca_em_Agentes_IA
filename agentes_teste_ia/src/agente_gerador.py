"""
Agente Gerador de Casos de Teste.

Papel (conforme agentes_teste_config.json): carregar/validar casos de
teste rotulados pela matriz (C1/C2/C3) e registra-los no repositorio de
evidencia ANTES de qualquer execucao pelo agente_alvo. Nunca executa o
payload — apenas gera/valida e entrega ao proximo agente.
"""

from __future__ import annotations

import json
from typing import List

from modelos import CasoTeste
from repositorio import RepositorioEvidencia


class AgenteGerador:

    IDENTIFICADORES_VALIDOS_PREFIXO = ("C1-", "C2-", "C3-")

    def __init__(self, repositorio: RepositorioEvidencia):
        self.repositorio = repositorio

    def carregar_bateria(self, caminho_json: str) -> List[CasoTeste]:
        with open(caminho_json, "r", encoding="utf-8") as f:
            bruto = json.load(f)

        casos: List[CasoTeste] = []
        for item in bruto:
            caso = CasoTeste.from_dict(item)
            self._validar_escopo(caso)
            casos.append(caso)
            # guardrail "sempre": registrar no repositorio antes do uso
            self.repositorio.registrar_caso(caso.to_dict())

        return casos

    def _validar_escopo(self, caso: CasoTeste) -> None:
        if not caso.matriz_id.startswith(self.IDENTIFICADORES_VALIDOS_PREFIXO):
            raise ValueError(
                f"Caso {caso.id_caso} fora do escopo da matriz oficial "
                f"(matriz_id={caso.matriz_id}); requer aprovacao humana "
                f"antes de ser gerado (guardrail agente_gerador)."
            )
