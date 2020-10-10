# FTX Telegram rss

Periodic monitoring funding rates from [FTX](https://ftx.com/) exchange and
broadcast it through telegram

Esta é uma solução proposta para um exercício específico; mais detalhes sobre os
requisitos do exercício,
[aqui](https://www.notion.so/Simple-FTX-Funding-Alerter-7b0c2400a58c4b2d887e615a281be708).

A solução foi concebida como um módulo único, com 3 classes principais:
***Futures***, ***TelegramReport*** e ***CheckAndReport***; A partir de uma
instância de ***CheckAndReport***, é possível rodar um "sentinela" para escutar
e transmitir **funding rates** da FTX, tanto pelo console, quanto pelo
[*telegram*](#Configurando-o-bot-telegram)

Uma versão segue rodando em desenvolvimento, emitindo relatórios a cada 1h para
um grupo no telegram; [clique](https://t.me/joinchat/BsaPrRylCgEXuNZFrKQDCQ)
para se juntar ao grupo e acompanhar os relatórios.

## Rodando no modo Padrão

### 1 - Dependências

É necessário ter **python 3.8** ou superior instalado na máquina. Também é
considerada uma boa prática isolar o ambiente em que se roda uma aplicação; é
altamente recomendado o uso do [poetry](https://python-poetry.org/) para tal.

A partir daqui, todas as instruções valem para ambientes **linux**. Em ambientes
windows ou mac - desde que o python esteja instalado - tudo deve funcionar
normalmente se for consumido em um ambiente com as dependências do projeto
instaladas.

1.1 - Para instalar o poetry, faça:

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

... ou, se preferir utilizar o pip:

    pip install poetry

### 2 - Baixando e instalando

2.1 - Baixe o projeto ou clone-o para seu computador, fazendo:

    git clone https://github.com/marcusmello/ftx-telegram-rss.git

2.2 - Navegue até a pasta do projeto:

    cd ftx-telegram-rss/

2.3 - Instale as dependências:

    poetry install

### 3 - Rodando o programa

3.1 - Abra um terminal python com as dependências instaladas num ambiente
virtual fazendo:

    poetry run python

3.2 - Importe a classe responsável pelo monitoramento e *report*:

```python
from ftx_telegram_rss import CheckAndReport
```

3.3 - Crie uma instância "***check_and_report***":

```python
check_and_report = CheckAndReport()
```

3.4 - Rode com:

```python
check_and_report.run()
```

Se preferir, é possível rodar no [jupyter notebook](#Rodando-no-Jupyter-Notebook).

## Rodando com configurações customizadas

É possível adicionar configurações personalizadas, alterando o comportamento do
"sentinela", como a taxa com a qual os relatórios são emitidos.

Para isto, basta abrir o arquivo de texto *".env"*, atribuindo os valores
desejados às variáveis de ambiente.
