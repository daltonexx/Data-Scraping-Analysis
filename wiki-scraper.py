import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

# ---------------------------------------------------------
# PASSO 0: PREPARAÇÃO
# ---------------------------------------------------------
url_base = "https://pt.wikipedia.org"
url_inicial = f"{url_base}/wiki/Neymar" 

headers = {
    'User-Agent': 'ProjetoLaboratorioPUCRS'
}

pasta_html = "paginas_html"
os.makedirs(pasta_html, exist_ok=True)

# ---------------------------------------------------------
# PASSO 1: BAIXAR A PÁGINA INICIAL E ENCONTRAR LINKS
# ---------------------------------------------------------
print("Baixando a página inicial...")
response = requests.get(url_inicial, headers=headers)

if response.status_code == 200:
    html_content = response.text
    
    with open(f"{pasta_html}/pagina_inicial.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    soup = BeautifulSoup(html_content, 'html.parser')
    
    tags_a = soup.find_all('a', href=True)
    links_internos = []

    for tag in tags_a:
        href = tag['href']
        
        # Flexibilizando o filtro para pegar links absolutos e relativos
        if '/wiki/' in href:
            # Pega apenas a parte do artigo (depois do /wiki/)
            parte_final = href.split('/wiki/')[-1]
            # Remove âncoras de sessão (ex: Brasil#História vira apenas Brasil)
            parte_final = parte_final.split('#')[0]
            
            # Verifica se não é página especial (sem os ":" no nome do artigo) e não é o Neymar
            if ':' not in parte_final and parte_final != 'Neymar' and parte_final != '':
                links_internos.append(f"/wiki/{parte_final}")


    # Remove duplicatas
    links_internos = list(set(links_internos))
    # links_internos = sorted(set(links_internos))  # Aqui é opcional, já que o original sempre vai trazer os links em ordem aleatória, entretanto não é necessário se for baixar todos os links

    # Limitando a 5 links para não demorar no teste (remova o [:5] depois para a entrega final)

    links_para_baixar = links_internos[:5] 
    print(f"Foram encontrados {len(links_internos)} links internos válidos!")
    print(f"Vamos baixar {len(links_para_baixar)} links para teste...\n")
    
    # ---------------------------------------------------------
    # PASSO 2: BAIXAR O HTML DE CADA LINK
    # ---------------------------------------------------------
    for index, link in enumerate(links_para_baixar):
        url_completa = f"{url_base}{link}"
        print(f"Baixando ({index+1}/{len(links_para_baixar)}): {url_completa}")
        
        res = requests.get(url_completa, headers=headers)
        
        nome_arquivo = link.replace("/", "_") + ".html"
        caminho_arquivo = f"{pasta_html}/{nome_arquivo}"
        
        with open(caminho_arquivo, "w", encoding="utf-8") as file:
            file.write(res.text)
            
        time.sleep(1) 
        
    print("\nTodos os HTMLs foram baixados com sucesso! Iniciando extração local (Passo 3)...")

    # ---------------------------------------------------------
    # PASSO 3: EXTRAÇÃO DE DADOS LOCAIS E GERAÇÃO DOS CSVS
    # ---------------------------------------------------------
    dados_paginas = []
    dados_imagens = []

    arquivos_html = os.listdir(pasta_html)

    for arquivo in arquivos_html:
        if arquivo.endswith(".html"):
            caminho_completo = os.path.join(pasta_html, arquivo)
            
            with open(caminho_completo, "r", encoding="utf-8") as file:
                conteudo = file.read()
                
            soup_local = BeautifulSoup(conteudo, 'html.parser')
            
            # 1. Título
            titulo = soup_local.title.string if soup_local.title else "Sem título"
            
            # 2. Primeiro Parágrafo (ignora tags vazias ou muito curtas)
            paragrafos = soup_local.find_all('p')
            primeiro_paragrafo = ""
            for p in paragrafos:
                texto = p.text.strip()
                if len(texto) > 20: 
                    primeiro_paragrafo = texto
                    break
                    
            # 3. Extração das Imagens
            tags_img = soup_local.find_all('img')
            for img in tags_img:
                src = img.get('src')
                if src:
                    # Arrumando caminhos de imagens quebrados
                    if src.startswith('//'):
                        src = f"https:{src}"
                    elif src.startswith('/'):
                        src = f"https://pt.wikipedia.org{src}"
                        
                    dados_imagens.append({
                        'pagina_origem': titulo,
                        'link_imagem': src,
                        'timestamp': datetime.now()
                    })
                    
            # 4. Extração dos Links Internos (mesma lógica usada no Crawler)
            tags_a_local = soup_local.find_all('a', href=True)
            links_internos_local = []
            for tag in tags_a_local:
                href_local = tag['href']
                if '/wiki/' in href_local:
                    parte_final = href_local.split('/wiki/')[-1].split('#')[0]
                    if ':' not in parte_final and parte_final != '':
                        links_internos_local.append(f"/wiki/{parte_final}")
                        
            links_internos_local = list(set(links_internos_local))
            
            # Estruturando os dados da página
            dados_paginas.append({
                'titulo': titulo,
                'primeiro_paragrafo': primeiro_paragrafo,
                'links_internos': ", ".join(links_internos_local),
                'timestamp': datetime.now()
            })

    # Exportando os dados limpos e raspados para CSV
    df_paginas = pd.DataFrame(dados_paginas)
    df_imagens = pd.DataFrame(dados_imagens)

    df_paginas.to_csv("dados_paginas.csv", index=False, encoding='utf-8')
    df_imagens.to_csv("dados_imagens.csv", index=False, encoding='utf-8')

    print("\nSUCESSO! Os arquivos 'dados_paginas.csv' e 'dados_imagens.csv' foram criados na pasta do seu projeto.")

else:
    print(f"Erro! A Wikipédia bloqueou o acesso. Código: {response.status_code}")