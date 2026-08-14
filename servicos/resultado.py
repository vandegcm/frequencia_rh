from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResultadoProcessamento:
    """Resultado exibivel de uma operacao solicitada pelo menu."""

    sucesso: bool
    mensagem: str
    arquivos_gerados: tuple[Path, ...] = ()
