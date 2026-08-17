import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from modelos.funcionario import FuncionarioFrequencia, FuncionarioMeta4
from utils.formatadores import obter_caminho_unico

class GeradorRelatorios:

    @staticmethod
    def gerar_lista_frequencia(pasta_salvar: str, funcionarios: List[FuncionarioFrequencia]):
        # Agrupar por fonte e setor
        grupos = {}
        arquivos_gerados = []
        for f in funcionarios:
            chave = (f.fonte, f.setor)
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(f)

        for (fonte, setor), lista_funcs in grupos.items():
            nome_arquivo = obter_caminho_unico(pasta_salvar, f'lista de frequencia - {fonte} - {setor}', 'xlsx')
            arquivo = xlsxwriter.Workbook(nome_arquivo)
            
            formato_cabecalho = arquivo.add_format({
                'text_wrap': True, 'bold': True, 'border': 1, 
                'valign': 'vcenter', 'align': 'center', 'bg_color': '#d9d9d9',
                'font_name': 'Calibri', 'font_size': 11
            })
            formato_corpo = arquivo.add_format({
                'text_wrap': True, 'border': 1, 'valign': 'vcenter',
                'font_name': 'Calibri', 'font_size': 11
            })
            
            aba = arquivo.add_worksheet(name=f'{fonte}_{setor}')
            aba.set_column(0, 0, 5)
            aba.set_column(1, 1, 40)
            
            cabecalhos = [
                'ID', 'Nome', 'R.G.', 'Admissão', 'Função', 'Dias Trabalhados',
                'Afastamentos A', 'Afastamentos B', 'Atraso Saída', 'Dias Falta',
                'Adicional Noturno',
                'HE (50% D)', 'HE (50% N)', 'HE (100%)', 'Sobreaviso', 'Observações', 'Frequência'
            ]
            for col, cabecalho in enumerate(cabecalhos):
                aba.write(0, col, cabecalho, formato_cabecalho)
                
            linha_ref = 1
            for func in lista_funcs:
                aba.write(linha_ref, 0, func.id_funcionario, formato_corpo)
                aba.write(linha_ref, 1, func.nome, formato_corpo)
                aba.write(linha_ref, 2, func.rg, formato_corpo)
                aba.write(linha_ref, 3, func.admissao, formato_corpo)
                aba.write(linha_ref, 4, func.funcao, formato_corpo)
                linha_ref += 1
                
            arquivo.close()

            arquivos_gerados.append(Path(nome_arquivo))

        return tuple(arquivos_gerados)

    @staticmethod
    def gerar_boletim(pasta_salvar: str, funcionarios: List[FuncionarioFrequencia], tipo: str = 'boletim'):
        nome_arquivo = obter_caminho_unico(pasta_salvar, f'Boletim_{tipo}', 'xlsx')
        arquivo = xlsxwriter.Workbook(nome_arquivo)
        
        normal = arquivo.add_format({
            'text_wrap': True, 'font_name': 'Calibri', 'font_size': 11,
            'border': 1, 'valign': 'vcenter', 'align': 'center'
        })
        
        aba = arquivo.add_worksheet()
        aba.set_landscape()
        
        linha_ref = 0
        for func in funcionarios:
            if tipo == 'faltas':
                aba.write(linha_ref, 0, f'{func.nome}\n{func.funcao}', normal)
                aba.write(linha_ref, 1, func.rg, normal)
                aba.write(linha_ref, 2, func.dias_falta, normal)
                aba.write(linha_ref, 3, func.atraso_saida, normal)
                aba.write(linha_ref, 4, func.observacoes, normal)
                aba.write(linha_ref, 5, func.frequencia, normal)
                linha_ref += 1
            else:
                aba.write(linha_ref, 0, func.nome, normal)
                aba.write(linha_ref, 1, func.rg, normal)
                aba.write(linha_ref, 2, func.funcao, normal)
                aba.write(linha_ref, 3, func.dias_trabalhados, normal)
                aba.write(linha_ref, 4, func.frequencia, normal)
                linha_ref += 1
                
        arquivo.close()
        return Path(nome_arquivo)
        
    @staticmethod
    def gerar_relatorio_meta4(pasta_salvar: str, funcionarios_meta4: List[FuncionarioMeta4]):
        nome_arquivo = obter_caminho_unico(pasta_salvar, 'META4_relatorio_funcionarios', 'xlsx')
        arquivo = xlsxwriter.Workbook(nome_arquivo)
        aba = arquivo.add_worksheet()
        linha_ref = 1
        
        for func in funcionarios_meta4:
            coluna_ref = 0
            dados = [
                func.nome, func.rg, func.n_id, func.t_emp, func.nascimento, func.pis, func.cpf,
                func.admissao, func.id_ato_formal, func.carga_horaria, func.cargo, func.funcao,
                func.classe, func.referencia_classe, func.cidade, func.estado, func.quadro
            ]
                     
            for dado in dados:
                aba.write(linha_ref, coluna_ref, dado)
                coluna_ref += 1
                
            salario_base = [l[2] for l in func.lancamentos if l[0] == '1005']
            gr1056 = [l[2] for l in func.lancamentos if l[0] == '1056']
            gr1059 = [l[2] for l in func.lancamentos if l[0] == '1059']
            
            if salario_base:
                aba.write(linha_ref, coluna_ref, float(salario_base[0]))
            coluna_ref += 1
            if gr1056:
                aba.write(linha_ref, coluna_ref, float(gr1056[0]))
            coluna_ref += 1
            if gr1059:
                aba.write(linha_ref, coluna_ref, float(gr1059[0]))
            
            linha_ref += 1
            
        arquivo.close()
        return Path(nome_arquivo)
        
    @staticmethod
    def gerar_relatorio_extras(pasta_salvar: str, lista_ids: List[int], l_bh: Dict[str, List[float]],
                               l_hr: Dict[str, List[float]], dados_funcionarios_meta4: List[FuncionarioMeta4],
                               calculos: Dict[int, dict], problemas: dict):
        agora = datetime.now()
        nome_arquivo = obter_caminho_unico(
            pasta_salvar, 
            f'relatorio de extras {agora.day}-{agora.month}-{agora.year}-{agora.hour}-{agora.minute}-{agora.second}', 
            'xlsx'
        )
        
        arquivo = xlsxwriter.Workbook(nome_arquivo)
        aba = arquivo.add_worksheet('HE')
        
        formato_cabecalho = arquivo.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D9D9D9'
        })
        formato_normal = arquivo.add_format({'align': 'center', 'valign': 'vcenter'})
        formato_monetario = arquivo.add_format({
            'align': 'center', 'valign': 'vcenter', 'num_format': '0.00'
        })

        formato_cabecalho_total_horas = arquivo.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#E4DFEC'
        })
        formato_total_horas = arquivo.add_format({
            'align': 'center', 'valign': 'vcenter', 'bg_color': '#E4DFEC'
        })

        formato_cabecalho_valor_pago = arquivo.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#CCC1D9'
        })
        formato_valor_pago = arquivo.add_format({
            'align': 'center', 'valign': 'vcenter', 'bg_color': '#CCC1D9',
            'num_format': '0.00'
        })

        formato_cabecalho_total_pago = arquivo.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
            'text_wrap': True, 'bg_color': '#92D050'
        })
        formato_total_pago = arquivo.add_format({
            'align': 'center', 'valign': 'vcenter', 'bg_color': '#92D050',
            'num_format': '0.00'
        })

        formato_cabecalho_saldo = arquivo.add_format({
            'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#FFC000'
        })
        formato_saldo = arquivo.add_format({
            'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFC000'
        })

        # Largura e formato-base de cada bloco.
        aba.set_column('A:A', 13, formato_normal)
        aba.set_column('B:B', 35, formato_normal)
        aba.set_column('C:C', 30, formato_normal)
        aba.set_column('D:D', 13, formato_normal)
        aba.set_column('E:E', 17, formato_monetario)
        aba.set_column('F:F', 13, formato_monetario)
        aba.set_column('G:G', 14, formato_monetario)
        aba.set_column('H:O', 13, formato_normal)
        aba.set_column('P:S', 13, formato_total_horas)
        aba.set_column('T:W', 13, formato_normal)
        aba.set_column('X:AA', 13, formato_valor_pago)
        aba.set_column('AB:AC', 13, formato_total_pago)
        aba.set_column('AD:AG', 13, formato_saldo)
        
        # ---------------------------------------------------------
        # CABEÇALHOS (LINHA 1 E 2)
        # ---------------------------------------------------------
        # 1. Informações do Servidor (A-G)
        aba.merge_range(0, 0, 0, 6, 'Informações do Servidor', formato_cabecalho)
        headers_info = [
            'ID', 'Nome', 'Função', 'Quadro', 'Valor Sobreaviso',
            'Valor Hora', 'Limite Pagar'
        ]
        for i, h in enumerate(headers_info):
            aba.write(1, i, h, formato_cabecalho)
            
        # 2. Banco de Horas (H-K)
        aba.merge_range(0, 7, 0, 10, 'Banco de Horas', formato_cabecalho)
        headers_bh = ['50 D', '50 N', '100%', 'SA']
        for i, h in enumerate(headers_bh):
            aba.write(1, i+7, h, formato_cabecalho)
            
        # 3. Horas Realizadas (L-O)
        aba.merge_range(0, 11, 0, 14, 'Horas Realizadas', formato_cabecalho)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+11, h, formato_cabecalho)
            
        # 4. Total Horas (P-S)
        aba.merge_range(0, 15, 0, 18, 'Total Horas', formato_cabecalho_total_horas)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+15, h, formato_cabecalho_total_horas)
            
        # 5. Horas a Pagar (T-W), equivalente ao antigo "Pagar Calculo"
        aba.merge_range(0, 19, 0, 22, 'Horas a Pagar', formato_cabecalho)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+19, h, formato_cabecalho)

        # 6. Valor Pago (X-AA)
        aba.merge_range(0, 23, 0, 26, 'Valor Pago', formato_cabecalho_valor_pago)
        headers_valor = ['50 D', '50 N', '100 %', 'SA.']
        for i, h in enumerate(headers_valor):
            aba.write(1, i+23, h, formato_cabecalho_valor_pago)

        # 7. Total Pago (AB) e Dif. (AC), mesclados verticalmente
        aba.merge_range(0, 27, 1, 27, 'Total Pago', formato_cabecalho_total_pago)
        aba.merge_range(0, 28, 1, 28, 'Dif.', formato_cabecalho_total_pago)

        # 8. Saldo Atualizado (AD-AG)
        aba.merge_range(0, 29, 0, 32, 'Saldo Atualizado', formato_cabecalho_saldo)
        for i, h in enumerate(headers_valor):
            aba.write(1, i+29, h, formato_cabecalho_saldo)

        # ---------------------------------------------------------
        # PREENCHIMENTO DOS DADOS
        # ---------------------------------------------------------
        linha_ref = 2
        chaves_horas = ('50d', '50n', '100', 'sa')
        for i, id_func in enumerate(lista_ids):
            tem_horas = any(
                (l_bh[chave][i] or 0) != 0 or (l_hr[chave][i] or 0) != 0
                for chave in chaves_horas
            )
            if not tem_horas:
                continue

            if id_func not in calculos:
                aba.write(linha_ref, 0, id_func)
                aba.write(linha_ref, 1, "DADOS INDISPONIVEIS")
            elif calculos[id_func].get('duplo_vinculo'):
                aba.write(linha_ref, 0, id_func)
                aba.write(linha_ref, 1, calculos[id_func]['nome'])
                aba.write(linha_ref, 2, "DUPLO VÍNCULO")
            else:
                c = calculos[id_func]
                
                # Informações
                aba.write(linha_ref, 0, id_func)
                aba.write(linha_ref, 1, c['nome'])
                aba.write(linha_ref, 2, c['funcao'])
                aba.write(linha_ref, 3, c['quadro'])
                aba.write(linha_ref, 4, c['valor_hora_sobreaviso'], formato_monetario)
                aba.write(linha_ref, 5, c['valor_hora'], formato_monetario)
                aba.write(linha_ref, 6, c['rt'], formato_monetario)
                
                # Banco de Horas
                aba.write(linha_ref, 7, l_bh['50d'][i])
                aba.write(linha_ref, 8, l_bh['50n'][i])
                aba.write(linha_ref, 9, l_bh['100'][i])
                aba.write(linha_ref, 10, l_bh['sa'][i])
                
                # Horas Realizadas
                aba.write(linha_ref, 11, l_hr['50d'][i])
                aba.write(linha_ref, 12, l_hr['50n'][i])
                aba.write(linha_ref, 13, l_hr['100'][i])
                aba.write(linha_ref, 14, l_hr['sa'][i])

                # Total Horas (Banco de Horas + Horas Realizadas)
                linha_excel = linha_ref + 1
                for deslocamento, chave in enumerate(chaves_horas):
                    coluna_banco = xl_col_to_name(7 + deslocamento)
                    coluna_realizadas = xl_col_to_name(11 + deslocamento)
                    total_horas = l_bh[chave][i] + l_hr[chave][i]
                    aba.write_formula(
                        linha_ref,
                        15 + deslocamento,
                        f'={coluna_banco}{linha_excel}+{coluna_realizadas}{linha_excel}',
                        formato_total_horas,
                        total_horas,
                    )
                
                # Horas a Pagar
                aba.write(linha_ref, 19, c['horas_pagas']['50d'])
                aba.write(linha_ref, 20, c['horas_pagas']['50n'])
                aba.write(linha_ref, 21, c['horas_pagas']['100'])
                aba.write(linha_ref, 22, c['horas_pagas']['sa'])
                
                # Valor Pago
                valores_pagos = (
                    c['val_he_diurna'], c['val_he_noturna'],
                    c['val_he_dom_fer'], c['val_sobreaviso']
                )
                for deslocamento, valor in enumerate(valores_pagos):
                    aba.write(linha_ref, 23 + deslocamento, valor, formato_valor_pago)

                # Total Pago e diferença restante para o limite
                total_pago = sum(valores_pagos)
                aba.write_formula(
                    linha_ref, 27, f'=SUM(X{linha_excel}:AA{linha_excel})',
                    formato_total_pago, total_pago
                )
                aba.write_formula(
                    linha_ref, 28, f'=G{linha_excel}-AB{linha_excel}',
                    formato_total_pago, c['rt'] - total_pago
                )

                # Saldo Atualizado (Total Horas - Horas a Pagar)
                for deslocamento, chave in enumerate(chaves_horas):
                    coluna_total = xl_col_to_name(15 + deslocamento)
                    coluna_pagar = xl_col_to_name(19 + deslocamento)
                    aba.write_formula(
                        linha_ref,
                        29 + deslocamento,
                        f'={coluna_total}{linha_excel}-{coluna_pagar}{linha_excel}',
                        formato_saldo,
                        c['novo_saldo'][chave],
                    )
                
            linha_ref += 1
            
        arquivo.close()
        return Path(nome_arquivo)
