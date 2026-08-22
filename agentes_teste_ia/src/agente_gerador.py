"""
Agente Gerador de Casos de Teste.

Papel (config: agentes.agente_gerador): carregar/validar casos de teste
rotulados pela matriz e registra-los no repositorio de evidencia ANTES
de qualquer execucao pelo agente_alvo. Nunca executa o payload.

Toda a validacao de escopo vem de ConfigAgentesTeste — nenhum prefixo
de matriz ou regra de guardrail e hardcoded aqui (ver config_loader.py,
metodo prefixos_validos_por_camada).
"""

from __future__ import annotations

import json
from typing import List

from modelos import CasoTeste
from repositorio import RepositorioEvidencia
from config_loader import ConfigAgentesTeste


class AgenteGerador:

    def __init__(self, repositorio: RepositorioEvidencia, config: ConfigAgentesTeste):
        self.repositorio = repositorio
        self.config = config
        self._prefixos_validos = config.prefixos_validos_por_camada()  # ex.: {"C1-": "Camada 1", ...}
        self._guardrails = config.guardrails("agente_gerador")

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
        prefixo_encontrado = next(
            (p for p in self._prefixos_validos if caso.matriz_id.startswith(p)), None
        )
        if prefixo_encontrado is None:
            gatilhos = self._guardrails.get("gatilhos_de_escalonamento", [])
            raise ValueError(
                f"Caso {caso.id_caso} fora do escopo da matriz oficial "
                f"(matriz_id={caso.matriz_id}); prefixos aceitos: "
                f"{sorted(self._prefixos_validos)}. "
                f"Gatilho de escalonamento aplicavel (config): {gatilhos}"
            )

        # Consistencia entre o prefixo do matriz_id e o campo 'camada' declarado
        camada_esperada = self._prefixos_validos[prefixo_encontrado]
        if caso.camada != camada_esperada:
            raise ValueError(
                f"Caso {caso.id_caso} declara camada='{caso.camada}', mas "
                f"matriz_id='{caso.matriz_id}' corresponde a '{camada_esperada}'."
            )
