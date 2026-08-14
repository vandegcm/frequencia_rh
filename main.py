import logging
import os
from pathlib import Path

from config import PASTA_FUNEAS, PASTA_SESA
from servicos.processador_frequencia import ProcessadorFrequencia
from servicos.resultado import ResultadoProcessamento
from utils.formatadores import validar_competencia


logging.basicConfig(
    filename=Path(__file__).resolve().with_name("frequencia_rh.log"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOGGER = logging.getLogger(__name__)


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def solicitar_competencia():
    """Solicita e valida a competencia, retornando (MM, AAAA) ou None."""
    mes = input("Digite o Mes (MM): ")
    ano = input("Digite o Ano (AAAA): ")
    try:
        return validar_competencia(mes, ano)
    except ValueError as erro:
        input(f"Competencia invalida: {erro} Pressione Enter para continuar...")
        return None


def mostrar_resultado(resultado: ResultadoProcessamento):
    prefixo = "SUCESSO" if resultado.sucesso else "ATENCAO"
    print(f"\n{prefixo}: {resultado.mensagem}")
    if resultado.arquivos_gerados:
        print("Arquivo(s) gerado(s):")
        for caminho in resultado.arquivos_gerados:
            print(f"- {caminho}")
    input("\nPressione Enter para continuar...")


def executar_operacao(operacao, *args):
    """Executa uma operacao do menu sem encerrar a aplicacao em caso de falha."""
    try:
        resultado = operacao(*args)
    except (FileNotFoundError, PermissionError, KeyError, ValueError) as erro:
        resultado = ResultadoProcessamento(False, str(erro))
    except Exception:
        LOGGER.exception("Falha inesperada durante o processamento")
        resultado = ResultadoProcessamento(
            False,
            "Ocorreu uma falha inesperada. Consulte frequencia_rh.log ou contate o suporte.",
        )
    mostrar_resultado(resultado)


def tela_fonte(nome_fonte, pasta_referencia):
    while True:
        limpar_tela()
        print(f"------------------------ {nome_fonte} ------------------------")
        print("[L] - Gerar Planilhas para Lancamento dos Dados")
        print("[B] - Gerar Boletim")
        print("[F] - Gerar Boletim de Faltas")
        print("[V] - Voltar")

        opcao = input("Selecione a Opcao: ").strip().upper()

        if opcao in {'L', 'B', 'F'}:
            competencia = solicitar_competencia()
            if competencia is None:
                continue
            mes, ano = competencia

            if opcao == 'L':
                executar_operacao(
                    ProcessadorFrequencia.processar_lista_frequencia,
                    pasta_referencia,
                    mes,
                    ano,
                )
            else:
                tipo = 'boletim' if opcao == 'B' else 'faltas'
                executar_operacao(
                    ProcessadorFrequencia.processar_boletins,
                    pasta_referencia,
                    mes,
                    ano,
                    tipo,
                )
        elif opcao == 'V':
            break
        else:
            input("Opcao invalida. Pressione Enter para continuar...")


def tela_funeas():
    tela_fonte("FUNEAS", PASTA_FUNEAS)


def tela_sesa():
    tela_fonte("SESA", PASTA_SESA)


def tela_extras():
    while True:
        limpar_tela()
        print("------------------------ HORAS EXTRAS ------------------------")
        print("[P] - Processar Relatorios Meta4 / Extras")
        print("[V] - Voltar")

        opcao = input("Selecione a Opcao: ").strip().upper()

        if opcao == 'P':
            competencia = solicitar_competencia()
            if competencia is None:
                continue
            mes, ano = competencia
            print(f"Iniciando processamento de extras para {mes}/{ano}...")

            from servicos.processador_extras import ProcessadorExtras

            executar_operacao(
                ProcessadorExtras.processar_relatorios_meta4_extras,
                int(mes),
                int(ano),
            )
        elif opcao == 'V':
            break
        else:
            input("Opcao invalida. Pressione Enter para continuar...")


def main():
    while True:
        limpar_tela()
        print("======== SISTEMA DE PROCESSAMENTO DE DADOS (RH) ========")
        print("[F] - FUNEAS")
        print("[S] - SESA")
        print("[E] - HORAS EXTRAS (META4)")
        print("[SAIR] - Sair do programa")

        opcao = input("Selecione uma Opcao: ").strip().upper()

        if opcao == 'F':
            tela_funeas()
        elif opcao == 'S':
            tela_sesa()
        elif opcao == 'E':
            tela_extras()
        elif opcao == 'SAIR':
            break
        else:
            input("Opcao invalida. Pressione Enter para continuar...")


if __name__ == "__main__":
    main()
