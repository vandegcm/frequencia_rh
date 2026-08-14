import os
from pathlib import Path
from servicos.leitor_planilhas import LeitorPlanilhas
from servicos.gerador_relatorios import GeradorRelatorios
from servicos.resultado import ResultadoProcessamento
from utils.formatadores import tratar_pasta, validar_competencia

class ProcessadorFrequencia:
    
    @staticmethod
    def organizar_alfabeticamente(funcionarios):
        return sorted(funcionarios, key=lambda f: f.nome)

    @staticmethod
    def processar_lista_frequencia(pasta_referencia: str, mes: str, ano: str):
        mes, ano = validar_competencia(mes, ano)
        arquivo_funcionarios = os.path.join(pasta_referencia, 'funcionarios.xlsx')
        if not os.path.exists(arquivo_funcionarios):
            return ResultadoProcessamento(
                False,
                f"Arquivo de funcionarios nao encontrado: {arquivo_funcionarios}",
            )
            
        funcs_sesa, funcs_funeas = LeitorPlanilhas.buscar_funcionarios_xlsx(arquivo_funcionarios)
        fonte = Path(pasta_referencia).name.upper()
        if fonte not in {"SESA", "FUNEAS"}:
            return ResultadoProcessamento(
                False,
                "A pasta de referencia deve terminar com SESA ou FUNEAS.",
            )
        funcionarios_processar = funcs_sesa if fonte == "SESA" else funcs_funeas
        
        pasta_ano = tratar_pasta(pasta_referencia, ano, criar_prontos=False)
        pasta_salvar = tratar_pasta(pasta_ano, mes, criar_prontos=True)
        
        arquivos = GeradorRelatorios.gerar_lista_frequencia(
            pasta_salvar, funcionarios_processar
        )
        if not arquivos:
            return ResultadoProcessamento(
                False,
                f"Nenhum funcionario ativo da fonte {fonte} foi encontrado.",
            )
        return ResultadoProcessamento(
            True,
            f"Lista de frequencia gerada para {mes}/{ano}.",
            arquivos,
        )

    @staticmethod
    def processar_boletins(pasta_referencia: str, mes: str, ano: str, tipo: str = 'boletim'):
        mes, ano = validar_competencia(mes, ano)
        if tipo not in {"boletim", "faltas"}:
            raise ValueError("O tipo deve ser 'boletim' ou 'faltas'.")

        pasta_mes = Path(pasta_referencia) / ano / mes
        pasta_prontos = pasta_mes / 'prontos'
        
        if not os.path.exists(pasta_prontos) or len(os.listdir(pasta_prontos)) == 0:
            return ResultadoProcessamento(
                False,
                f"Nenhuma lista preenchida foi encontrada em: {pasta_prontos}",
            )
            
        todos_funcionarios = []
        for arquivo in sorted(os.listdir(pasta_prontos)):
            if (
                arquivo.lower().endswith(".xlsx")
                and not arquivo.startswith("~$")
                and 'lista de frequencia' in arquivo.lower()
            ):
                funcs = LeitorPlanilhas.ler_dados_frequencia(
                    str(pasta_prontos / arquivo)
                )
                todos_funcionarios.extend(funcs)

        if not todos_funcionarios:
            return ResultadoProcessamento(
                False,
                f"Nao ha planilhas de frequencia validas em: {pasta_prontos}",
            )
                
        funcionarios_alf = ProcessadorFrequencia.organizar_alfabeticamente(todos_funcionarios)
        arquivo_gerado = GeradorRelatorios.gerar_boletim(
            str(pasta_mes), funcionarios_alf, tipo
        )
        nome = "Boletim de faltas" if tipo == "faltas" else "Boletim"
        return ResultadoProcessamento(
            True,
            f"{nome} gerado para {mes}/{ano}.",
            (arquivo_gerado,),
        )
