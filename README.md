# Sistema de Processamento de Dados do RH

Aplicacao de terminal para preparar listas de frequencia, consolidar boletins da
SESA/FUNEAS e calcular horas extras a partir dos relatorios META4.

> A aplicacao processa dados funcionais e pessoais. Restrinja o acesso às
> planilhas, não envie arquivos reais ao Git e siga as regras internas de
> proteção de dados da instituição.

## Requisitos

- Windows com acesso às pastas de rede configuradas;
- Python 3.14 (versão validada: 3.14.4);
- Microsoft Excel ou programa compatível para preencher os arquivos gerados.

## Instalação

Abra o PowerShell na pasta do projeto e execute:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Se o PowerShell impedir a ativação do ambiente, execute a aplicação diretamente:

```powershell
.\.venv\Scripts\python.exe main.py
```

Edite o arquivo `.env` antes do primeiro uso. Ele contém caminhos locais e não
deve ser compartilhado nem enviado ao repositório.

## Configuração do `.env`

| Variável | Finalidade |
| --- | --- |
| `PASTA_CONTROLE_FREQUENCIA` | Pasta que contém `SESA` e `FUNEAS`. |
| `PASTA_RELATORIOS_META4` | Raiz dos arquivos CSV exportados do META4. |
| `PASTA_EXTRAS` | Raiz da planilha e dos resultados de horas extras. |
| `HOSPITAL_REGIONAL` | Nome exato da unidade nos CSVs do META4. |
| `CODIGO_SALARIO_BASE` | Rubrica usada para identificar salário-base e duplo vínculo. |
| `CODIGOS_SV1` | Rubricas separadas por vírgula que compõem a Somatória 1. |
| `CODIGOS_SV2` | Rubricas separadas por vírgula que compõem a Somatória 2. |
| `INCLUI_SOBREAVISO_NO_REDUTOR` | Define se sobreaviso participa do limite do redutor. |

Os códigos de rubrica devem ser numéricos, sem repetições. Para a opção booleana
são aceitos `true/false`, `yes/no`, `on/off`, `1/0` e `sim/nao`.

## Estrutura dos arquivos

### Frequência SESA e FUNEAS

Cada fonte deve possuir seu cadastro `funcionarios.xlsx`:

```text
PASTA_CONTROLE_FREQUENCIA
├── SESA
│   └── funcionarios.xlsx
└── FUNEAS
    └── funcionarios.xlsx
```

O cadastro usa a primeira aba, com cabeçalho na linha 1 e dados desde a linha 2:

| Coluna | Conteúdo |
| --- | --- |
| A | ID |
| B | Função |
| C | Nome |
| D | RG |
| E | Admissão |
| F | Exoneração |
| G | Setor |
| H | Fonte (`SESA` ou `FUNEAS`) |
| I | Ativo (`sim` para incluir) |

Ao gerar as listas, a aplicação cria:

```text
SESA ou FUNEAS
└── AAAA
    └── MM
        └── prontos
            └── lista de frequencia - FONTE - SETOR.xlsx
```

Preencha a lista sem alterar o nome da aba, os cabeçalhos ou a ordem das
colunas. Os dados começam na linha 2. Para gerar boletins, mantenha os arquivos
preenchidos na pasta `prontos`.

### Horas extras/META4

Para a competência `08/2026`, por exemplo, a estrutura esperada é:

```text
PASTA_RELATORIOS_META4
└── 2026
    └── 08 - Agosto
        └── relatorios.csv

PASTA_EXTRAS
└── 2026
    └── 08 - Agosto
        └── Planilha Extras.xlsm
```

Também é aceito o mês sem zero à esquerda, como `8 - Agosto`. Apenas arquivos
`.csv` da pasta META4 são lidos. A `Planilha Extras.xlsm` deve conter as abas:

- `GROUND_ZERO`: banco anterior de horas;
- `FERIADOS`: datas consideradas no cálculo;
- `PYTHON`: plantões comuns;
- `PYTHON_SA`: plantões de sobreaviso.

Não altere os nomes dessas abas. O relatório final é criado na mesma pasta da
`Planilha Extras.xlsm`, com nome único para não substituir arquivos existentes.

## Como usar

Inicie a aplicação:

```powershell
.\.venv\Scripts\python.exe main.py
```

No menu principal:

- `F`: abre as operações da FUNEAS;
- `S`: abre as operações da SESA;
- `E`: processa horas extras do META4;
- `SAIR`: encerra o programa.

Nos menus SESA/FUNEAS:

1. Use `L` para gerar as listas que os setores preencherão.
2. Informe mês de `1` a `12` e ano com quatro dígitos.
3. Depois de receber as listas preenchidas na pasta `prontos`, use `B` para o
   boletim geral ou `F` para o boletim de faltas.

Em Horas Extras, use `P`, informe a competência e aguarde a confirmação. Uma
operação bem-sucedida mostra os caminhos exatos dos arquivos criados. Mensagens
com `ATENCAO` indicam que nenhum relatório válido foi produzido.

## Problemas comuns

- **Arquivo `funcionarios.xlsx` não encontrado:** confira a pasta da fonte e o
  valor de `PASTA_CONTROLE_FREQUENCIA`.
- **Nenhuma lista preenchida:** confirme que os `.xlsx` estão na pasta
  `AAAA\MM\prontos` e conservam `lista de frequencia` no nome.
- **Pastas da competência não encontradas:** confira o ano, o nome do mês e os
  caminhos configurados no `.env`.
- **Aba obrigatória ausente:** restaure o nome original da aba na planilha de
  extras.
- **Permissão negada:** feche a planilha no Excel e confirme acesso de escrita à
  pasta de destino.
- **Falha inesperada:** consulte `frequencia_rh.log` na pasta da aplicação e
  encaminhe-o ao suporte sem anexar as planilhas com dados pessoais.

## Verificação técnica

Com o ambiente virtual ativado:

```powershell
python -m unittest discover -s tests -v
python -m pip check
```

Antes de publicar, confirme com `git status` que `.env`, `.venv`, `.idea`,
`__pycache__`, logs e planilhas operacionais não fazem parte da entrega.
