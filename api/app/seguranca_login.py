"""Proteção contra força bruta no login.

Conta as tentativas erradas por (IP + e-mail) e por e-mail. Passou do limite dentro da
janela de tempo, a API responde 429 até a janela andar — mesmo com a senha certa.
Fica na memória do processo (a API roda em uma instância só no Render), sem banco extra.
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, status

JANELA_SEGUNDOS = 15 * 60
LIMITE_POR_IP_E_EMAIL = 5   # quem erra a própria senha algumas vezes
LIMITE_POR_EMAIL = 20       # vários IPs atacando a mesma conta


class LimitadorLogin:
    def __init__(self) -> None:
        self._falhas: dict[str, deque[float]] = defaultdict(deque)
        self._trava = Lock()

    @staticmethod
    def _chaves(ip: str, email: str) -> list[tuple[str, int]]:
        email = email.strip().lower()
        return [(f"ip:{ip}|{email}", LIMITE_POR_IP_E_EMAIL), (f"email:{email}", LIMITE_POR_EMAIL)]

    def _limpar_antigas(self, fila: deque[float], agora: float) -> None:
        while fila and agora - fila[0] > JANELA_SEGUNDOS:
            fila.popleft()

    def verificar(self, ip: str, email: str) -> None:
        agora = time.monotonic()
        with self._trava:
            for chave, limite in self._chaves(ip, email):
                fila = self._falhas[chave]
                self._limpar_antigas(fila, agora)
                if len(fila) >= limite:
                    espera = int(JANELA_SEGUNDOS - (agora - fila[0])) + 1
                    raise HTTPException(
                        status.HTTP_429_TOO_MANY_REQUESTS,
                        f"Muitas tentativas de login. Tente de novo em {max(1, espera // 60)} min.",
                        headers={"Retry-After": str(espera)},
                    )

    def registrar_falha(self, ip: str, email: str) -> None:
        agora = time.monotonic()
        with self._trava:
            for chave, _ in self._chaves(ip, email):
                self._falhas[chave].append(agora)
            if len(self._falhas) > 10_000:  # não deixa a memória crescer sem fim
                for chave in [c for c, f in self._falhas.items() if not f or agora - f[-1] > JANELA_SEGUNDOS]:
                    del self._falhas[chave]

    def registrar_sucesso(self, ip: str, email: str) -> None:
        with self._trava:
            self._falhas.pop(self._chaves(ip, email)[0][0], None)

    def limpar(self) -> None:
        with self._trava:
            self._falhas.clear()


limitador = LimitadorLogin()
