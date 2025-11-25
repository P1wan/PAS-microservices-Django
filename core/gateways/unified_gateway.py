from dataclasses import dataclass
from typing import List, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExternalData:
    discentes: List[Dict[str, Any]]
    disciplinas: List[Dict[str, Any]]
    livros: List[Dict[str, Any]]
    sucesso: bool
    erros: List[str]


class UnifiedGateway:
    TIMEOUT = 5.0

    ENDPOINTS = {
        'discentes': 'https://rmi6vdpsq8.execute-api.us-east-2.amazonaws.com/msAluno',
        'disciplinas': 'https://sswfuybfs8.execute-api.us-east-2.amazonaws.com/disciplinaServico/msDisciplina',
        'livros': 'https://qiiw8bgxka.execute-api.us-east-2.amazonaws.com/acervo/biblioteca',
    }

    @classmethod
    def consumir_todos_dados(cls) -> ExternalData:
        discentes = []
        disciplinas = []
        livros = []
        erros = []

        try:
            resp = requests.get(cls.ENDPOINTS['discentes'], timeout=cls.TIMEOUT)
            if resp.ok:
                discentes = resp.json()
                logger.info(f"Consumidos {len(discentes)} discentes")
            else:
                erros.append(f"Erro ao buscar discentes: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar discentes: {e}")
            logger.error(f"Erro discentes: {e}")

        try:
            resp = requests.get(cls.ENDPOINTS['disciplinas'], timeout=cls.TIMEOUT)
            if resp.ok:
                disciplinas = resp.json()
                logger.info(f"Consumidas {len(disciplinas)} disciplinas")
            else:
                erros.append(f"Erro ao buscar disciplinas: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar disciplinas: {e}")
            logger.error(f"Erro disciplinas: {e}")

        try:
            resp = requests.get(cls.ENDPOINTS['livros'], timeout=cls.TIMEOUT)
            if resp.ok:
                livros = resp.json()
                logger.info(f"Consumidos {len(livros)} livros")
            else:
                erros.append(f"Erro ao buscar livros: HTTP {resp.status_code}")
        except Exception as e:
            erros.append(f"Erro ao buscar livros: {e}")
            logger.error(f"Erro livros: {e}")

        sucesso = len(discentes) > 0 or len(disciplinas) > 0 or len(livros) > 0

        return ExternalData(
            discentes=discentes,
            disciplinas=disciplinas,
            livros=livros,
            sucesso=sucesso,
            erros=erros,
        )
