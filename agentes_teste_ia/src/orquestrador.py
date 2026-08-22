"""
Orquestrador do ciclo de teste completo:
agente_gerador -> agente_alvo -> agente_avaliador -> repositorio_evidencia

O agentes_teste_config.json e carregado e validado UMA VEZ aqui
(ConfigAgentesTeste) e injetado nos tres agentes — nenhum deles le o
arquivo por conta propria nem duplica seu conteudo em Python.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone

from agente_gerador import AgenteGerador
from agente_alvo import AgenteAlvo
from agente_avaliador import AgenteAvaliador
from config_loader import ConfigAgentesTeste
from mock_tools import SandboxToolkit
from repositorio import RepositorioEvidencia


def executar_ciclo(caminho_casos: str, diretorio_saida: str, caminho_config: str,
                    familia_modelo_gerador: str = "familia-A",
                    familia_modelo_alvo: str = "familia-A-em-teste",
                    familia_modelo_avaliador: str = "familia-B") -> dict:
    config = ConfigAgentesTeste(caminho_config)
    repo = RepositorioEvidencia(diretorio_saida)

    gerador = AgenteGerador(repo, config)
    alvo = AgenteAlvo(config)
    avaliador = AgenteAvaliador(
        config,
        familia_modelo_gerador=familia_modelo_gerador,
        familia_modelo_alvo=familia_modelo_alvo,
        familia_modelo_avaliador=familia_modelo_avaliador,
    )

    casos = gerador.carregar_bateria(caminho_casos)

    vereditos = []
    for caso in casos:
        execucao = alvo.executar(caso)
        repo.registrar_execucao(execucao.to_dict())

        veredito = avaliador.avaliar(caso, execucao)
        repo.registrar_veredito(veredito.to_dict())

        vereditos.append(veredito)

    relatorio = _montar_relatorio(casos, vereditos, caminho_config)

    caminho_relatorio = os.path.join(diretorio_saida, "relatorio_final.json")
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    return relatorio


def _montar_relatorio(casos, vereditos, caminho_config) -> dict:
    total = len(vereditos)
    por_veredito = Counter(v.veredito for v in vereditos)
    por_severidade = Counter(v.severidade for v in vereditos)
    por_camada = Counter(c.camada for c in casos)

    pendentes_revisao = [
        {
            "id_caso": v.id_caso,
            "severidade": v.severidade,
            "justificativa": v.justificativa,
        }
        for v in vereditos
        if v.revisao_humana_exigida and v.revisao_humana_status == "pendente"
    ]

    conflitos_sinalizados = [v.id_caso for v in vereditos if v.conflito_de_interesse_sinalizado]

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "config_utilizado": caminho_config,
        "total_casos_executados": total,
        "distribuicao_por_camada": dict(por_camada),
        "distribuicao_por_veredito": dict(por_veredito),
        "distribuicao_por_severidade": dict(por_severidade),
        "bloqueio_de_release": len(pendentes_revisao) > 0,
        "achados_pendentes_revisao_humana": pendentes_revisao,
        "casos_com_conflito_de_interesse_sinalizado": conflitos_sinalizados,
    }
