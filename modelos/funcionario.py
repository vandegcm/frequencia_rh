from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class FuncionarioFrequencia:
    nome: str
    rg: str
    admissao: str
    funcao: str
    dias_trabalhados: Optional[int] = None
    afastamentos_a: Optional[str] = None
    afastamentos_b: Optional[str] = None
    atraso_saida: Optional[str] = None
    dias_falta: Optional[int] = None
    adicional_noturno: Optional[float] = None
    he_50_d: Optional[float] = None
    he_50_n: Optional[float] = None
    he_100: Optional[float] = None
    sobreaviso: Optional[float] = None
    observacoes: Optional[str] = None
    frequencia: Optional[str] = None
    setor: Optional[str] = None
    fonte: Optional[str] = None
    id_funcionario: Optional[int] = None
    exoneracao: Optional[str] = None

@dataclass
class FuncionarioMeta4:
    nome: str
    rg: str
    n_id: int
    t_emp: str
    nascimento: str
    pis: str
    cpf: str
    admissao: str
    id_ato_formal: str
    carga_horaria: str
    cargo: str
    funcao: str
    classe: str
    referencia_classe: str
    cidade: str
    estado: str
    quadro: str
    lancamentos: List[tuple] = field(default_factory=list)
