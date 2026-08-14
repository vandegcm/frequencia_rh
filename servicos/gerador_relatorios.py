import xlsxwriter
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
        
        # Ajustar a largura das colunas (todas para 13)
        aba.set_column('A:AB', 13, formato_normal)
        
        # ---------------------------------------------------------
        # CABEÇALHOS (LINHA 1 E 2)
        # ---------------------------------------------------------
        # 1. Informações do Servidor (A-D)
        aba.merge_range(0, 0, 0, 3, 'Informações do Servidor', formato_cabecalho)
        headers_info = ['ID', 'Nome', 'Função', 'Quadro']
        for i, h in enumerate(headers_info):
            aba.write(1, i, h, formato_cabecalho)
            
        # 2. Banco de Horas (E-H)
        aba.merge_range(0, 4, 0, 7, 'Banco Anterior', formato_cabecalho)
        headers_bh = ['50 D', '50 N', '100%', 'SA']
        for i, h in enumerate(headers_bh):
            aba.write(1, i+4, h, formato_cabecalho)
            
        # 3. Horas Realizadas (I-L)
        aba.merge_range(0, 8, 0, 11, 'Horas Realizadas', formato_cabecalho)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+8, h, formato_cabecalho)
            
        # 4. Horas a Pagar (M-P)
        aba.merge_range(0, 12, 0, 15, 'Horas a Pagar', formato_cabecalho)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+12, h, formato_cabecalho)
            
        # 5. Valores Brutos R$ (Q-T)
        aba.merge_range(0, 16, 0, 19, 'Valores Brutos', formato_cabecalho)
        headers_bruto = ['HE Diurna', 'HE Noturna', 'HE 100%', 'Sobreaviso']
        for i, h in enumerate(headers_bruto):
            aba.write(1, i+16, h, formato_cabecalho)
            
        # 6. Totais (U) - Mesclado verticalmente
        aba.merge_range(0, 20, 1, 20, 'Total Bruto', formato_cabecalho)
        
        # 7. Limites e Redutor (V-W)
        aba.merge_range(0, 21, 0, 22, 'Descontos', formato_cabecalho)
        headers_desc = ['Limite RT', 'Redutor']
        for i, h in enumerate(headers_desc):
            aba.write(1, i+21, h, formato_cabecalho)
            
        # 8. Total Líquido (X) - Mesclado verticalmente
        aba.merge_range(0, 23, 1, 23, 'Total Líquido', formato_cabecalho)
        
        # 9. Saldo Atualizado (Y-AB)
        aba.merge_range(0, 24, 0, 27, 'Saldo Atualizado', formato_cabecalho)
        for i, h in enumerate(headers_bh):
            aba.write(1, i+24, h, formato_cabecalho)

        # ---------------------------------------------------------
        # PREENCHIMENTO DOS DADOS
        # ---------------------------------------------------------
        linha_ref = 2
        for i, id_func in enumerate(lista_ids):
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
                
                # Banco de Horas
                aba.write(linha_ref, 4, l_bh['50d'][i])
                aba.write(linha_ref, 5, l_bh['50n'][i])
                aba.write(linha_ref, 6, l_bh['100'][i])
                aba.write(linha_ref, 7, l_bh['sa'][i])
                
                # Horas Realizadas
                aba.write(linha_ref, 8, l_hr['50d'][i])
                aba.write(linha_ref, 9, l_hr['50n'][i])
                aba.write(linha_ref, 10, l_hr['100'][i])
                aba.write(linha_ref, 11, l_hr['sa'][i])
                
                # Horas a Pagar
                aba.write(linha_ref, 12, c['horas_pagas']['50d'])
                aba.write(linha_ref, 13, c['horas_pagas']['50n'])
                aba.write(linha_ref, 14, c['horas_pagas']['100'])
                aba.write(linha_ref, 15, c['horas_pagas']['sa'])
                
                # Valores Brutos
                aba.write(linha_ref, 16, c['val_he_diurna'])
                aba.write(linha_ref, 17, c['val_he_noturna'])
                aba.write(linha_ref, 18, c['val_he_dom_fer'])
                aba.write(linha_ref, 19, c['val_sobreaviso'])
                
                # Total Bruto
                aba.write(linha_ref, 20, c['total_bruto_geral'])
                
                # Descontos
                aba.write(linha_ref, 21, c['rt'])
                aba.write(linha_ref, 22, c['redutor_aplicado'])
                
                # Total Liquido
                aba.write(linha_ref, 23, c['total_liquido'])
                
                # Saldo Atualizado
                aba.write(linha_ref, 24, c['novo_saldo']['50d'])
                aba.write(linha_ref, 25, c['novo_saldo']['50n'])
                aba.write(linha_ref, 26, c['novo_saldo']['100'])
                aba.write(linha_ref, 27, c['novo_saldo']['sa'])
                
            linha_ref += 1
            
        arquivo.close()
        return Path(nome_arquivo)
