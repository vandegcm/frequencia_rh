from dataclasses import dataclass
from datetime import datetime

@dataclass
class Plantao:
    id_funcionario: int
    entrada: datetime
    saida_autorizada: datetime
