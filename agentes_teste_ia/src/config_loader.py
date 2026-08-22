"""
Carregador do agentes_teste_config.json — fonte unica de verdade para
guardrails, criterios de severidade, ferramentas permitidas e schema de
saida dos tres agentes.

Nenhum agente deve conter guardrail, criterio de severidade ou lista de
ferramenta permitida hardcoded em Python: tudo vem deste arquivo. Isso
garante que uma mudanca no config (ex.: alterar quais severidades
exigem revisao humana) se reflita no comportamento real sem precisar
tocar no codigo dos agentes — o proprio problema que motivou este
modulo (ver conversa: o config existia mas nao era lido por ninguem).
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Set


CHAVES_TOPO_OBRIGATORIAS = (
    "documento", "regras_globais", "agentes", "schema_saida_json",
    "criterios_severidade", "ambiente_sandbox",
)

AGENTES_OBRIGATORIOS = ("agente_gerador", "agente_alvo", "agente_avaliador")

SUBCHAVES_AGENTE_OBRIGATORIAS = (
    "purpose", "guardrails", "tools", "knowledge", "behavior",
)


class ConfigInvalidaError(Exception):
    """Levantada quando o JSON de configuracao esta ausente ou incompleto."""


class ConfigAgentesTeste:
    """Acesso tipado e validado ao agentes_teste_config.json."""

    def __init__(self, caminho_json: str):
        self._caminho = caminho_json
        with open(caminho_json, "r", encoding="utf-8") as f:
            self._dados = json.load(f)
        self._validar_estrutura()

    # ------------------------------------------------------------------
    # Validacao — falha rapido se o config estiver incompleto, em vez de
    # deixar um agente rodar com guardrail ausente por erro de digitacao
    # ou edicao manual do JSON.
    # ------------------------------------------------------------------
    def _validar_estrutura(self) -> None:
        faltando_topo = [c for c in CHAVES_TOPO_OBRIGATORIAS if c not in self._dados]
        if faltando_topo:
            raise ConfigInvalidaError(
                f"{self._caminho}: chaves de topo ausentes: {faltando_topo}"
            )

        agentes = self._dados.get("agentes", {})
        faltando_agentes = [a for a in AGENTES_OBRIGATORIOS if a not in agentes]
        if faltando_agentes:
            raise ConfigInvalidaError(
                f"{self._caminho}: definicao de agente ausente: {faltando_agentes}"
            )

        for nome, definicao in agentes.items():
            faltando = [c for c in SUBCHAVES_AGENTE_OBRIGATORIAS if c not in definicao]
            if faltando:
                raise ConfigInvalidaError(
                    f"{self._caminho}: agente '{nome}' sem as chaves {faltando}"
                )

    # ------------------------------------------------------------------
    # Acesso a regras globais
    # ------------------------------------------------------------------
    def proibicoes_absolutas(self) -> List[str]:
        return list(self._dados["regras_globais"]["proibicoes_absolutas"])

    def severidades_que_exigem_revisao_humana(self) -> Set[str]:
        return set(self._dados["regras_globais"]["severidades_que_exigem_revisao_humana"])

    def criterios_severidade(self) -> Dict[str, str]:
        return dict(self._dados["criterios_severidade"])

    def ambiente_sandbox(self) -> dict:
        return dict(self._dados["ambiente_sandbox"])

    # ------------------------------------------------------------------
    # Acesso por agente
    # ------------------------------------------------------------------
    def agente(self, nome: str) -> dict:
        try:
            return self._dados["agentes"][nome]
        except KeyError as exc:
            raise ConfigInvalidaError(f"Agente '{nome}' nao definido no config.") from exc

    def guardrails(self, nome: str) -> dict:
        return dict(self.agente(nome)["guardrails"])

    def tools_permitidas(self, nome: str) -> List[str]:
        return list(self.agente(nome)["tools"]["permitidas"])

    def tools_proibidas(self, nome: str) -> List[str]:
        return list(self.agente(nome)["tools"]["proibidas"])

    def autonomia(self, nome: str) -> str:
        return self.agente(nome)["behavior"]["autonomia"]

    def limites_de_escopo(self, nome: str) -> List[str]:
        return list(self.agente(nome)["guardrails"].get("limites_de_escopo", []))

    def schema_saida(self, nome: str) -> dict:
        return dict(self._dados["schema_saida_json"][nome])

    # ------------------------------------------------------------------
    # Derivacao: prefixos validos de matriz_id por camada.
    #
    # O config nao lista prefixos como "C1-" explicitamente — eles sao
    # derivados do texto de agentes.agente_gerador.tipos_de_teste
    # ("Camada 1 — ...", "Camada 2 — ...", ...). Isso evita hardcodar a
    # tupla de prefixos em Python: se uma Camada 4 for adicionada ao
    # config no futuro, o agente_gerador passa a aceita-la sem mudanca
    # de codigo.
    # ------------------------------------------------------------------
    def prefixos_validos_por_camada(self) -> Dict[str, str]:
        tipos = self.agente("agente_gerador").get("tipos_de_teste", [])
        mapa = {}
        for descricao in tipos:
            m = re.match(r"Camada\s+(\d+)", descricao)
            if m:
                numero = m.group(1)
                mapa[f"C{numero}-"] = f"Camada {numero}"
        if not mapa:
            raise ConfigInvalidaError(
                "Nao foi possivel derivar prefixos validos de "
                "agentes.agente_gerador.tipos_de_teste — verifique o formato "
                "('Camada N — ...') no config."
            )
        return mapa
