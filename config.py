import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega sempre o .env localizado ao lado deste modulo. Variaveis definidas no
# sistema operacional continuam tendo precedencia sobre o arquivo local.
load_dotenv(dotenv_path=Path(__file__).resolve().with_name(".env"))


def _ler_lista_codigos(nome: str, padrao: str) -> tuple[str, ...]:
    """Lê uma lista de códigos numéricos separados por vírgula."""
    valor = os.getenv(nome, padrao)
    partes = tuple(codigo.strip() for codigo in valor.split(','))

    if not partes or any(not codigo for codigo in partes):
        raise ValueError(f"{nome} contém um código de rubrica vazio.")
    codigos = partes
    if any(not codigo.isdigit() for codigo in codigos):
        raise ValueError(f"{nome} deve conter somente códigos numéricos separados por vírgula.")
    if len(set(codigos)) != len(codigos):
        raise ValueError(f"{nome} contém códigos duplicados.")

    return codigos


def _ler_booleano(nome: str, padrao: bool) -> bool:
    """Lê booleanos do ambiente sem aceitar valores ambíguos."""
    valor = os.getenv(nome, str(padrao)).strip().lower()
    verdadeiros = {'1', 'true', 'yes', 'on', 'sim'}
    falsos = {'0', 'false', 'no', 'off', 'nao', 'não'}

    if valor in verdadeiros:
        return True
    if valor in falsos:
        return False
    raise ValueError(
        f"{nome} deve ser um booleano: true/false, yes/no, on/off, 1/0 ou sim/não."
    )

PASTA_CONTROLE_FREQUENCIA = Path(os.getenv("PASTA_CONTROLE_FREQUENCIA", r"R:\frequencia"))
PASTA_SESA = PASTA_CONTROLE_FREQUENCIA / "SESA"
PASTA_FUNEAS = PASTA_CONTROLE_FREQUENCIA / "FUNEAS"

PASTA_RELATORIOS_META4 = Path(os.getenv("PASTA_RELATORIOS_META4", r"R:\frequencia\HORAS EXTRAS\den\relatoriosmeta4"))
PASTA_EXTRAS = Path(os.getenv("PASTA_EXTRAS", r"R:\frequencia\HORAS EXTRAS\den"))

HOSPITAL_REGIONAL = os.getenv("HOSPITAL_REGIONAL", "HOSPITAL REGIONAL DE FRANCISCO BELTRAO")

# Política de composição das bases de horas extras.
CODIGO_SALARIO_BASE = os.getenv("CODIGO_SALARIO_BASE", "1005").strip()
CODIGOS_SV1 = _ler_lista_codigos("CODIGOS_SV1", "1005,1923,1056,1059")
CODIGOS_SV2 = _ler_lista_codigos("CODIGOS_SV2", "1005,1056,1059")
INCLUI_SOBREAVISO_NO_REDUTOR = _ler_booleano("INCLUI_SOBREAVISO_NO_REDUTOR", False)

if not CODIGO_SALARIO_BASE.isdigit():
    raise ValueError("CODIGO_SALARIO_BASE deve ser um código numérico.")
if CODIGO_SALARIO_BASE not in CODIGOS_SV1 or CODIGO_SALARIO_BASE not in CODIGOS_SV2:
    raise ValueError("CODIGO_SALARIO_BASE deve estar presente em CODIGOS_SV1 e CODIGOS_SV2.")
