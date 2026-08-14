"""
Calculadora de Horas Extras e Redutor — NRHS/SESA-PR
Baseada na Lei nº 18.136/2014 e Manual META4 (regras vigentes em 21/05/2026).

Uso:
    calc = CalculadoraHorasExtras(
        quadro="QPSS",       # "QPSS" ou "QPPE"
        carga=40,            # 40 ou 20 (horas semanais)
        base_sv1=3500,
        base_sv2=3000,
        he_diurna=10,        # horas
        he_dom_fer=0,        # horas
        he_noturna=0,        # horas
        sobreaviso=0,        # horas
        adc_noturno=0,       # horas
    )
    resultado = calc.calcular()
"""

from dataclasses import dataclass


@dataclass
class CalculadoraHorasExtras:
    # --- Fatores e multiplicadores fixos ---
    FT_ADC_NOTURNO: float = 1.14285
    FT_HE_NOTURNA: float = 1.3714
    MULT_HE_DIURNA: float = 1.5
    MULT_HE_DOMFER: float = 2.0
    MULT_SOBREAVISO: float = 0.3333
    MULT_ADC_NOTURNO: float = 0.20
    PERC_REDUTOR: float = 0.3333

    # --- Entradas ---
    quadro: str = "QPSS"
    carga: int | str = 40
    base_sv1: float = 0.0
    base_sv2: float = 0.0
    he_diurna: float = 0.0
    he_dom_fer: float = 0.0
    he_noturna: float = 0.0
    sobreaviso: float = 0.0
    adc_noturno: float = 0.0
    inclui_sobreaviso_no_redutor: bool = False

    def __post_init__(self) -> None:
        try:
            self.carga = int(str(self.carga).strip())
        except (TypeError, ValueError) as exc:
            raise ValueError("A carga horária deve ser 20 ou 40.") from exc

        if self.carga not in (20, 40):
            raise ValueError("A carga horária deve ser 20 ou 40.")

        self.quadro = str(self.quadro).strip().upper()

    @property
    def sv1(self) -> float:
        """Somatória 1, composta pelas rubricas configuradas no ambiente."""
        return self.base_sv1

    @property
    def sv2(self) -> float:
        """Somatória 2, composta pelas rubricas configuradas no ambiente."""
        return self.base_sv2

    @property
    def sv_principal(self) -> float:
        """Base principal usada no cálculo de H.E, conforme o quadro funcional."""
        return self.sv1 if self.quadro == "QPSS" else self.sv2

    @property
    def ch(self) -> int:
        """Divisor mensal (carga horária -> horas/mês)."""
        return 200 if self.carga == 40 else 100

    def val_he_diurna(self) -> float:
        return (self.sv_principal / self.ch) * self.he_diurna * self.MULT_HE_DIURNA

    def val_he_dom_fer(self) -> float:
        return (self.sv_principal / self.ch) * self.he_dom_fer * self.MULT_HE_DOMFER

    def val_he_noturna(self) -> float:
        return (
            (self.sv_principal / self.ch)
            * self.he_noturna
            * self.MULT_HE_DIURNA
            * self.FT_HE_NOTURNA
        )

    def val_sobreaviso(self) -> float:
        """Plantão sobreaviso usa sempre SV2, sem fator noturno."""
        return (self.sv2 / self.ch) * self.sobreaviso * self.MULT_SOBREAVISO

    def val_adc_noturno(self) -> float:
        """Adicional noturno usa obrigatoriamente SV1."""
        return (
            (self.sv1 / self.ch)
            * self.adc_noturno
            * self.MULT_ADC_NOTURNO
            * self.FT_ADC_NOTURNO
        )

    def she(self) -> float:
        """Somatória das horas extras, sem adicionais e sobreaviso."""
        return self.val_he_diurna() + self.val_he_dom_fer() + self.val_he_noturna()

    def base_redutor(self) -> float:
        """Valor sujeito ao teto, conforme a política de sobreaviso."""
        valor = self.she()
        if self.inclui_sobreaviso_no_redutor:
            valor += self.val_sobreaviso()
        return valor

    def rt(self) -> float:
        """Limite de 33,33% sobre SV1 (Redutor de Horas Extras)."""
        return self.sv1 * self.PERC_REDUTOR

    def redutor_aplicado(self) -> float:
        """Valor excedente ao limite, que é deduzido do total."""
        base_redutor, rt = self.base_redutor(), self.rt()
        return base_redutor - rt if base_redutor > rt else 0.0

    def total_bruto_geral(self) -> float:
        return self.she() + self.val_sobreaviso() + self.val_adc_noturno()

    def total_liquido(self) -> float:
        return self.total_bruto_geral() - self.redutor_aplicado()

    def calcular(self) -> dict:
        """Retorna um dicionário com todos os valores calculados."""
        return {
            "sv1": self.sv1,
            "sv2": self.sv2,
            "sv_principal": self.sv_principal,
            "ch": self.ch,
            "val_he_diurna": self.val_he_diurna(),
            "val_he_dom_fer": self.val_he_dom_fer(),
            "val_he_noturna": self.val_he_noturna(),
            "val_sobreaviso": self.val_sobreaviso(),
            "val_adc_noturno": self.val_adc_noturno(),
            "she": self.she(),
            "base_redutor": self.base_redutor(),
            "rt": self.rt(),
            "redutor_aplicado": self.redutor_aplicado(),
            "total_bruto_geral": self.total_bruto_geral(),
            "total_liquido": self.total_liquido(),
        }


if __name__ == "__main__":
    calc = CalculadoraHorasExtras(
        quadro="QPSS", carga=40, base_sv1=3500, base_sv2=3000, he_diurna=10
    )
    from pprint import pprint
    pprint(calc.calcular())
