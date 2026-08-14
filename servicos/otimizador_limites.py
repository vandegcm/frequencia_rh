from typing import Dict, Tuple

class OtimizadorLimites:
    @staticmethod
    def calcular_horas_a_pagar(calc, horas_totais: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Recebe a calculadora (já instanciada com os dados base do funcionário) e as horas totais (Banco + Realizadas).
        Retorna (horas_pagas, novo_banco).
        """
        # Obter o limite máximo permitido sem redutor (RT)
        limite_restante = calc.rt()

        # Obter valores financeiros unitários (o custo financeiro de 1 hora)
        # Atribuimos 1.0 hora e chamamos as funções da calculadora para obter o valor unitário dinamicamente
        calc.he_diurna = 1.0
        c_50d = calc.val_he_diurna()
        
        calc.he_noturna = 1.0
        c_50n = calc.val_he_noturna()
        
        calc.he_dom_fer = 1.0
        c_100 = calc.val_he_dom_fer()
        
        calc.sobreaviso = 1.0
        c_sa = calc.val_sobreaviso()
        
        # Limpar os contadores na calculadora
        calc.he_diurna = 0.0
        calc.he_noturna = 0.0
        calc.he_dom_fer = 0.0
        calc.sobreaviso = 0.0

        pagar = {'50d': 0.0, '50n': 0.0, '100': 0.0, 'sa': 0.0}
        banco = {'50d': 0.0, '50n': 0.0, '100': 0.0, 'sa': 0.0}

        # Lista de prioridades de pagamento (ordem em que tentamos alocar o teto)
        # O script original cortava na exata inversa disso (100% primeiro, etc).
        # A prioridade para PAGAR era: 50D -> 50N -> 100 -> SA
        prioridades = [
            ('50d', c_50d),
            ('50n', c_50n),
            ('100', c_100),
            ('sa', c_sa)
        ]

        for rubrica, custo_unitario in prioridades:
            qtde_total = horas_totais.get(rubrica, 0.0)
            
            # Se a rubrica for SA e a regra não incluir o SA no limite do redutor, ignora o teto financeiro
            if rubrica == 'sa' and not calc.inclui_sobreaviso_no_redutor:
                pagar[rubrica] = qtde_total
                banco[rubrica] = 0.0
                continue
                
            if custo_unitario <= 0 or qtde_total <= 0:
                pagar[rubrica] = qtde_total
                banco[rubrica] = 0.0
                continue

            custo_total = qtde_total * custo_unitario
            
            if custo_total <= limite_restante:
                # Cabe tudo no limite! Paga integral e banco recebe 0.
                pagar[rubrica] = qtde_total
                banco[rubrica] = 0.0
                limite_restante -= custo_total
            else:
                # O limite estourou. Fatiar e truncar em horas inteiras conforme original: int()
                qtde_paga = float(int(limite_restante / custo_unitario))
                
                # Prevenção: qtde_paga não pode ser maior que o qtde_total
                if qtde_paga > qtde_total:
                    qtde_paga = qtde_total
                    
                pagar[rubrica] = qtde_paga
                banco[rubrica] = qtde_total - qtde_paga
                limite_restante -= qtde_paga * custo_unitario

        return pagar, banco
