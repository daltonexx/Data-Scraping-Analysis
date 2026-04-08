# Data-Scraping-Analysis

Este repositório contém os scripts Python desenvolvidos para a disciplina de Coleta, Preparação e Análise de Dados. O objetivo central é aplicar técnicas de web scraping em dois cenários distintos:
1. **Ambiente controlado:** Wikipédia.
2. **Ambiente real:** IMDb.

## Passos para rodar o código

### 1. Instalar as dependências

Antes de rodar o código, crie e ative um ambiente virtual para isolar as dependências do projeto:

`python3 -m venv .venv`

`source .venv/bin/activate`

Depois, instale as bibliotecas externas responsáveis pelas requisições HTTP, parseamento de HTML e automação de navegador:

`pip install -r requirements.txt`

Se preferir instalar manualmente, o conjunto usado pelos scripts é:

`pip install requests beautifulsoup4 pandas selenium webdriver-manager`

### 2. Executar os scripts

O projeto foi dividido em dois scripts separados para garantir a estabilidade da execução. Você pode rodá-los na ordem que preferir.

#### Opção 1: Rodar o Scraper da Wikipédia (Tarefa 1)

Este script acessa um artigo inicial de uma pessoa famosa na Wikipédia, realiza a exploração de links e salva os dados estruturados.

Para executar, rode no terminal:

`python wiki-scraper.py`

**O que este script faz:**
* Baixa o HTML da página inicial e de seus links internos relacionados (apenas `/wiki/`).
* Lê os arquivos HTML salvos localmente e extrai: título da página, primeiro parágrafo, links de imagens e links internos.
* Gera e salva dois arquivos CSV (`dados_paginas.csv` e `dados_imagens.csv`) contendo os dados solicitados e uma coluna de timestamp indicando o momento da coleta.

> **⚠️ Aviso Importante sobre a Wikipedia:**
> A execução completa dessa tarefa pode levar cerca de 15 minutos. O código efetua pausas programadas para evitar o excesso de requisições e não estressar o servidor da Wikipedia.

#### Opção 2: Rodar o Scraper do IMDb (Tarefa 2)

Devido às pesadas proteções anti-bot do IMDb, este script utiliza a biblioteca **Selenium** para simular a navegação humana e acessar a lista dos 250 filmes com maiores avaliações.

Para esta tarefa, também é necessário ter o Google Chrome instalado no sistema (WSL/Linux). Se ainda não tiver, use:

`sudo apt-get update`

`sudo apt-get install -y wget gnupg`

`wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-linux-keyring.gpg`

`echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list`

`sudo apt-get update`

`sudo apt-get install -y google-chrome-stable`

Para executar, rode no terminal:

`python imdb-scraper.py`

**O que este script faz:**
* Abre uma instância automatizada do Google Chrome e acessa a página do Top 250 do IMDb.
* Rola a página para acionar o carregamento dinâmico (lazy loading) e coleta os links individuais dos filmes.
* Faz o scraping das páginas específicas de cada filme obtendo: título, ano, URL e imagem do pôster local, nota, gêneros e diretores.
* Exporta o resultado consolidado para um arquivo `top_filmes_imdb.json`.

> **⚠️ Aviso Importante sobre o IMDb:**
> A execução completa dessa tarefa pode levar de 15 a 20 minutos. O código efetua pausas programadas para evitar o excesso de requisições e não estressar o servidor do IMDb.