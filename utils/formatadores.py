import os

NOME_MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}


def validar_competencia(mes, ano) -> tuple[str, str]:
    """Valida e normaliza mes/ano para os formatos MM e AAAA."""
    mes_texto = str(mes).strip()
    ano_texto = str(ano).strip()

    if not mes_texto.isdigit() or not 1 <= int(mes_texto) <= 12:
        raise ValueError("O mes deve ser um numero entre 1 e 12.")
    if not ano_texto.isdigit() or len(ano_texto) != 4:
        raise ValueError("O ano deve possuir quatro digitos.")

    return f"{int(mes_texto):02d}", ano_texto

def limpar_nome_arquivo(nome_arquivo: str, extensao: str) -> str:
    substituicoes = ['/', '\\', ':', '*', '"', '?', '<', '>', '|']
    for sub in substituicoes:
        nome_arquivo = nome_arquivo.replace(sub, '-')
    return f"{nome_arquivo}.{extensao}"

def obter_caminho_unico(pasta_salvar: str, nome_base: str, extensao: str) -> str:
    nome_limpo = limpar_nome_arquivo(nome_base, extensao)
    arquivos_pasta = os.listdir(pasta_salvar) if os.path.exists(pasta_salvar) else []
    
    if nome_limpo not in arquivos_pasta:
        return os.path.join(pasta_salvar, nome_limpo)
    
    indice = 1
    while True:
        novo_nome = limpar_nome_arquivo(f"{nome_base} ({indice})", extensao)
        if novo_nome not in arquivos_pasta:
            return os.path.join(pasta_salvar, novo_nome)
        indice += 1

def tratar_pasta(*args: str, criar_prontos: bool = False) -> str:
    caminho = os.path.join(*args)
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        
    if criar_prontos:
        pasta_prontos = os.path.join(caminho, 'prontos')
        if not os.path.exists(pasta_prontos):
            os.makedirs(pasta_prontos)
            
    return caminho

def hora_para_decimal(tempo) -> float:
    return round(tempo.days * 24 + tempo.seconds / 3600, 2)
