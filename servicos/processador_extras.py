from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from pathlib import Path

from config import (
    PASTA_RELATORIOS_META4,
    PASTA_EXTRAS,
    CODIGO_SALARIO_BASE,
    CODIGOS_SV1,
    CODIGOS_SV2,
    INCLUI_SOBREAVISO_NO_REDUTOR,
)
from servicos.leitor_planilhas import LeitorPlanilhas
from utils.formatadores import hora_para_decimal
from servicos.gerador_relatorios import GeradorRelatorios
from servicos.resultado import ResultadoProcessamento
from calculadora_horas_extras import CalculadoraHorasExtras
from servicos.otimizador_limites import OtimizadorLimites
from utils.formatadores import validar_competencia

NOME_MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

class ProcessadorExtras:

    @staticmethod
    def calcular_bases_meta4(
        lancamentos,
        codigos_sv1=CODIGOS_SV1,
        codigos_sv2=CODIGOS_SV2,
    ) -> Tuple[float, float]:
        """Soma as vantagens do META4 que compõem cada base configurada."""
        codigos_configurados = set(codigos_sv1) | set(codigos_sv2)
        totais_por_codigo: Dict[str, float] = {}
        for codigo, _descricao, vantagem, _desconto in lancamentos:
            if codigo in codigos_configurados:
                totais_por_codigo[codigo] = (
                    totais_por_codigo.get(codigo, 0.0) + float(vantagem or 0.0)
                )

        sv1 = sum(totais_por_codigo.get(codigo, 0.0) for codigo in codigos_sv1)
        sv2 = sum(totais_por_codigo.get(codigo, 0.0) for codigo in codigos_sv2)
        return sv1, sv2

    @staticmethod
    def dividir_horas_plantao(feriados: List[datetime], inicio_plantao: datetime, fim_plantao: datetime) -> Tuple[timedelta, timedelta, timedelta]:
        inicio_comparar = datetime(inicio_plantao.year, inicio_plantao.month, inicio_plantao.day)
        fim_comparar = datetime(fim_plantao.year, fim_plantao.month, fim_plantao.day)
        
        ipd = (inicio_plantao.weekday() == 6)
        fpd = (fim_plantao.weekday() == 6)
        ipf = inicio_comparar in feriados
        fpf = fim_comparar in feriados

        meia_noite = datetime(inicio_plantao.year, inicio_plantao.month, inicio_plantao.day) + timedelta(days=1)
        hid0 = datetime(inicio_plantao.year, inicio_plantao.month, inicio_plantao.day, 5, 0)
        hin0 = datetime(inicio_plantao.year, inicio_plantao.month, inicio_plantao.day, 22, 0)
        hid1 = hid0 + timedelta(days=1)
        
        h_50_d = timedelta(0)
        h_50_n = timedelta(0)
        h_100 = timedelta(0)

        if not ipf and not fpf and not ipd and not fpd:
            if hid0 <= inicio_plantao < hin0 >= fim_plantao:
                h_50_d = fim_plantao - inicio_plantao
            elif hid0 <= inicio_plantao < hin0 < fim_plantao:
                h_50_d = hin0 - inicio_plantao
                if fim_plantao > hid1:
                    h_50_d += (fim_plantao - hid1)
                    h_50_n = hid1 - hin0
                else:
                    h_50_n = fim_plantao - hin0
            elif hin0 <= inicio_plantao:
                if fim_plantao <= hid1:
                    h_50_n = fim_plantao - inicio_plantao
                else:
                    h_50_n = hid1 - inicio_plantao
                    h_50_d = fim_plantao - hid1
            elif inicio_plantao < hid0 > fim_plantao:
                h_50_n = fim_plantao - inicio_plantao
            elif inicio_plantao < hid0 < fim_plantao:
                h_50_n = hid0 - inicio_plantao
                h_50_d = fim_plantao - hid0
                
        elif (ipd or ipf) and (fpd or fpf):
            h_100 = fim_plantao - inicio_plantao
            
        elif not (ipd or ipf) and (fpd or fpf):
            h_100 = fim_plantao - meia_noite
            if inicio_plantao < hin0:
                h_50_n = meia_noite - hin0
                h_50_d = hin0 - inicio_plantao
            else:
                h_50_n = meia_noite - inicio_plantao
                
        elif (ipd or ipf) and not (fpd or fpf):
            h_100 = meia_noite - inicio_plantao
            if fim_plantao < hid1:
                h_50_n = fim_plantao - meia_noite
            else:
                h_50_n = hid1 - meia_noite
                h_50_d = fim_plantao - hid1

        return h_50_d, h_50_n, h_100

    @staticmethod
    def processar_relatorios_meta4_extras(mes: int, ano: int):
        mes_normalizado, ano_normalizado = validar_competencia(mes, ano)
        mes = int(mes_normalizado)
        ano = int(ano_normalizado)
        nome_mes = NOME_MESES.get(mes, '')
        
        pasta_ano_relatorio = Path(PASTA_RELATORIOS_META4) / str(ano)
        pasta_ano_extras = Path(PASTA_EXTRAS) / str(ano)
        
        pasta_mes_relatorios = pasta_ano_relatorio / f"{mes:02d} - {nome_mes}"
        if not pasta_mes_relatorios.exists():
            pasta_mes_relatorios_alt = pasta_ano_relatorio / f"{mes} - {nome_mes}"
            if pasta_mes_relatorios_alt.exists():
                pasta_mes_relatorios = pasta_mes_relatorios_alt

        pasta_mes_extras = pasta_ano_extras / f"{mes:02d} - {nome_mes}"
        if not pasta_mes_extras.exists():
            pasta_mes_extras_alt = pasta_ano_extras / f"{mes} - {nome_mes}"
            if pasta_mes_extras_alt.exists():
                pasta_mes_extras = pasta_mes_extras_alt
        
        if not pasta_mes_relatorios.exists() or not pasta_mes_extras.exists():
            return ResultadoProcessamento(
                False,
                "Pastas da competencia nao encontradas. Verifique: "
                f"'{pasta_mes_relatorios}' e '{pasta_mes_extras}'.",
            )

        arquivo_extras = pasta_mes_extras / "Planilha Extras.xlsm"
        if not arquivo_extras.exists():
            return ResultadoProcessamento(
                False,
                f"Arquivo de horas extras nao encontrado: {arquivo_extras}",
            )

        print("Lendo dados do META4...")
        dados_meta4 = LeitorPlanilhas.ler_relatorios_meta4_csv(str(pasta_mes_relatorios))
        dict_meta4 = {func.n_id: func for func in dados_meta4}

        print("Lendo Planilha Extras.xlsm (Banco, Feriados e Plantões)...")
        saldo_banco_horas = LeitorPlanilhas.ler_banco_horas(str(arquivo_extras))
        feriados = LeitorPlanilhas.ler_feriados(str(arquivo_extras))
        plantoes_python = LeitorPlanilhas.ler_plantoes(str(arquivo_extras), 'PYTHON')
        plantoes_sa = LeitorPlanilhas.ler_plantoes(str(arquivo_extras), 'PYTHON_SA')
        
        lista_ids = []
        l_bh = {'50d': [], '50n': [], '100': [], 'sa': []}
        l_hr = {'50d': [], '50n': [], '100': [], 'sa': []}
        
        calculos = {}
        problemas = {'dados_indisponiveis': [], 'duplo_vinculo': []}

        # Processamento por funcionário (unindo todos os IDs encontrados)
        ids_todos = set(saldo_banco_horas.keys())
        ids_todos.update(plantoes_python.keys())
        ids_todos.update(plantoes_sa.keys())
        
        for id_func in sorted(ids_todos):
            bh_50d, bh_50n, bh_100, bh_sa = saldo_banco_horas.get(id_func, (0.0, 0.0, 0.0, 0.0))
            lista_ids.append(id_func)
            
            # Banco de horas
            l_bh['50d'].append(bh_50d)
            l_bh['50n'].append(bh_50n)
            l_bh['100'].append(bh_100)
            l_bh['sa'].append(bh_sa)
            
            # Horas realizadas (calculadas dos plantões)
            hr_50d_td = timedelta()
            hr_50n_td = timedelta()
            hr_100_td = timedelta()
            hr_sa_td = timedelta()
            
            for entrada, saida in plantoes_python.get(id_func, []):
                h_d, h_n, h_c = ProcessadorExtras.dividir_horas_plantao(feriados, entrada, saida)
                hr_50d_td += h_d
                hr_50n_td += h_n
                hr_100_td += h_c
                
            for entrada, saida in plantoes_sa.get(id_func, []):
                hr_sa_td += (saida - entrada)
                
            hr_50d = hora_para_decimal(hr_50d_td)
            hr_50n = hora_para_decimal(hr_50n_td)
            hr_100 = hora_para_decimal(hr_100_td)
            hr_sa = hora_para_decimal(hr_sa_td)
            
            l_hr['50d'].append(hr_50d)
            l_hr['50n'].append(hr_50n)
            l_hr['100'].append(hr_100)
            l_hr['sa'].append(hr_sa)

            # Usar a nova calculadora!
            if id_func in dict_meta4:
                func_meta4 = dict_meta4[id_func]
                
                salario_base = [
                    float(val)
                    for cod, _desc, val, _desc2 in func_meta4.lancamentos
                    if cod == CODIGO_SALARIO_BASE
                ]

                if len(salario_base) > 1:
                    calculos[id_func] = {'duplo_vinculo': True, 'nome': func_meta4.nome}
                    problemas['duplo_vinculo'].append(id_func)
                elif len(salario_base) == 1:
                    sv1, sv2 = ProcessadorExtras.calcular_bases_meta4(func_meta4.lancamentos)
                    
                    # Totais de horas (banco + realizadas)
                    ht_50d = bh_50d + hr_50d
                    ht_50n = bh_50n + hr_50n
                    ht_100 = bh_100 + hr_100
                    ht_sa = bh_sa + hr_sa
                    horas_totais = {'50d': ht_50d, '50n': ht_50n, '100': ht_100, 'sa': ht_sa}
                    
                    # Cria calculadora zerada de horas apenas para extrair as bases e limites
                    calc = CalculadoraHorasExtras(
                        quadro=func_meta4.quadro,
                        carga=func_meta4.carga_horaria,
                        base_sv1=sv1,
                        base_sv2=sv2,
                        inclui_sobreaviso_no_redutor=INCLUI_SOBREAVISO_NO_REDUTOR,
                    )
                    
                    # Otimiza o fatiamento!
                    horas_pagas, novo_saldo = OtimizadorLimites.calcular_horas_a_pagar(calc, horas_totais)
                    
                    # Repassa as horas limitadas para o cálculo real
                    calc.he_diurna = horas_pagas['50d']
                    calc.he_noturna = horas_pagas['50n']
                    calc.he_dom_fer = horas_pagas['100']
                    calc.sobreaviso = horas_pagas['sa']
                    
                    resultado = calc.calcular()
                    resultado['nome'] = func_meta4.nome
                    resultado['funcao'] = func_meta4.funcao
                    resultado['quadro'] = func_meta4.quadro
                    resultado['horas_pagas'] = horas_pagas
                    resultado['novo_saldo'] = novo_saldo
                    
                    calculos[id_func] = resultado
            else:
                problemas['dados_indisponiveis'].append(id_func)

        print(f"Gerando relatório Excel com base na CalculadoraHorasExtras...")
        arquivo_gerado = GeradorRelatorios.gerar_relatorio_extras(
            pasta_salvar=str(pasta_mes_extras),
            lista_ids=lista_ids,
            l_bh=l_bh,
            l_hr=l_hr,
            dados_funcionarios_meta4=dados_meta4,
            calculos=calculos,
            problemas=problemas
        )
        return ResultadoProcessamento(
            True,
            f"Relatorio de horas extras gerado para {mes:02d}/{ano}.",
            (arquivo_gerado,),
        )
