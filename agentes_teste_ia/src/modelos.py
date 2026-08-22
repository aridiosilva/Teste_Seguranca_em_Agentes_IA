"""
Modelos de dados alinhados ao `schema_saida_json` do arquivo
agentes_teste_config.json (framework de avaliacao de risco).

Cada dataclass corresponde a um dos tres registros trocados no
ciclo de teste: caso gerado -> execucao do alvo -> veredito do avaliador.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
import uuid


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CasoTeste:
    """Caso de teste produzido pelo agente_gerador."""

    id_caso: str
    matriz_id: str
    camada: str
    vetor_ataque: str
    descricao_teste: str
    resultado_esperado: str
    severidade_estimada: str
    fonte: str
    data_geracao: str
    variacao_nova: bool = False

    @staticmethod
    def from_dict(d: dict) -> "CasoTeste":
        campos_obrigatorios = [
            "id_caso", "matriz_id", "camada", "vetor_ataque",
            "descricao_teste", "resultado_esperado", "data_geracao",
        ]
        faltando = [c for c in campos_obrigatorios if c not in d]
        if faltando:
            raise ValueError(
                f"Caso de teste invalido (campos ausentes: {faltando}): {d}"
            )
        return CasoTeste(
            id_caso=d["id_caso"],
            matriz_id=d["matriz_id"],
            camada=d["camada"],
            vetor_ataque=d["vetor_ataque"],
            descricao_teste=d["descricao_teste"],
            resultado_esperado=d["resultado_esperado"],
            severidade_estimada=d.get("severidade_estimada", "Média"),
            fonte=d.get("fonte", "gerado internamente"),
            data_geracao=d["data_geracao"],
            variacao_nova=d.get("variacao_nova", False),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChamadaFerramenta:
    ferramenta: str
    parametros: dict
    mockada: bool = True
    bloqueada: bool = False
    motivo_bloqueio: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecucaoAlvo:
    """Execucao produzida pelo agente_alvo para um caso de teste."""

    id_execucao: str
    id_caso: str
    entrada_recebida: str
    resposta_completa: str
    timestamp: str
    ferramentas_chamadas: list = field(default_factory=list)

    @staticmethod
    def novo(id_caso: str, entrada_recebida: str, resposta_completa: str,
             ferramentas_chamadas: list) -> "ExecucaoAlvo":
        return ExecucaoAlvo(
            id_execucao=f"EXEC-{uuid.uuid4().hex[:8]}",
            id_caso=id_caso,
            entrada_recebida=entrada_recebida,
            resposta_completa=resposta_completa,
            timestamp=_timestamp(),
            ferramentas_chamadas=[f.to_dict() if isinstance(f, ChamadaFerramenta) else f
                                   for f in ferramentas_chamadas],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VeredictoAvaliador:
    """Veredito produzido pelo agente_avaliador para uma execucao."""

    id_veredito: str
    id_execucao: str
    id_caso: str
    veredito: str  # "aprovado" | "reprovado"
    severidade: str  # "Critica" | "Alta" | "Media" | "Baixa"
    criterio_aplicado: str
    justificativa: str
    conflito_de_interesse_sinalizado: bool
    revisao_humana_exigida: bool
    revisao_humana_status: str  # "pendente" | "confirmado" | "revertido" | "nao_aplicavel"
    timestamp: str

    @staticmethod
    def novo(id_execucao: str, id_caso: str, veredito: str, severidade: str,
              criterio_aplicado: str, justificativa: str,
              revisao_humana_exigida: bool,
              conflito_de_interesse_sinalizado: bool = False) -> "VeredictoAvaliador":
        return VeredictoAvaliador(
            id_veredito=f"VER-{uuid.uuid4().hex[:8]}",
            id_execucao=id_execucao,
            id_caso=id_caso,
            veredito=veredito,
            severidade=severidade,
            criterio_aplicado=criterio_aplicado,
            justificativa=justificativa,
            conflito_de_interesse_sinalizado=conflito_de_interesse_sinalizado,
            revisao_humana_exigida=revisao_humana_exigida,
            revisao_humana_status="pendente" if revisao_humana_exigida else "nao_aplicavel",
            timestamp=_timestamp(),
        )

    def to_dict(self) -> dict:
        return asdict(self)
