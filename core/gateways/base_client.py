from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional

import requests


@dataclass(slots=True)
class HttpResult:
    '''Resultado padronizado de uma chamada HTTP a serviço externo.'''

    ok: bool
    data: Any | None
    status_code: int | None
    error: str | None
    elapsed: float


class BaseHttpClient:
    '''Cliente HTTP simples com timeout e medição de tempo.'''

    def __init__(self, base_url: str, timeout: float = 3.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str = "", params: Optional[Mapping[str, str]] = None) -> HttpResult:
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        inicio = time.time()

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            elapsed = time.time() - inicio

            try:
                data: Any | None = resp.json()
            except Exception:
                data = resp.text

            if elapsed > self.timeout:
                print(f"[WARN] Tempo de resposta > {self.timeout}s: {elapsed:.2f}s ({url})")

            if resp.ok:
                return HttpResult(
                    ok=True,
                    data=data,
                    status_code=resp.status_code,
                    error=None,
                    elapsed=elapsed,
                )

            return HttpResult(
                ok=False,
                data=data,
                status_code=resp.status_code,
                error=f"Erro HTTP {resp.status_code} ao acessar {url}",
                elapsed=elapsed,
            )

        except requests.RequestException as exc:
            elapsed = time.time() - inicio
            return HttpResult(
                ok=False,
                data=None,
                status_code=None,
                error=f"Falha de rede ao acessar {url}: {exc}",
                elapsed=elapsed,
            )
