from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
import requests

# ---------------------------------------------------------
# PASSO 0: PREPARAÇÃO
# ---------------------------------------------------------
pasta_posters = "posters_imdb"
os.makedirs(pasta_posters, exist_ok=True)

print("Iniciando o navegador robô (Selenium)...")
# Configurando o Chrome
opcoes = Options() # Roda o Chrome em modo invisível (sem abrir a janela)

# Iniciando o navegador
servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico, options=opcoes)

url_top250 = "https://www.imdb.com/chart/top/"
filmes_dados = []

try:
# ---------------------------------------------------------
    # PASSO 1: PEGAR OS 250 LINKS
    # ---------------------------------------------------------
    print("Acessando o Top 250 do IMDb...")
    navegador.get(url_top250)
    
    # Pausa inicial para o site carregar a estrutura básica
    time.sleep(5) 
    
    print("Rolando a página para carregar todos os filmes...")
    # Fazemos um loop para o robô dar "scroll" até o fim da página aos poucos
    for i in range(1, 6):
        navegador.execute_script(f"window.scrollTo(0, document.body.scrollHeight * ({i}/5));")
        time.sleep(1.5) # Espera 1.5s entre cada rolagem para dar tempo de renderizar
        
    # Agora sim, com tudo carregado, pegamos o HTML da página inteira
    soup = BeautifulSoup(navegador.page_source, 'html.parser')
    links_filmes = []
    
    # Vamos caçar especificamente os links dos títulos (o IMDb usa essa classe hoje)
    tags_a = soup.find_all('a', class_='ipc-title-link-wrapper', href=True)
    
    # Plano B: se a classe falhar, pegamos todos os links e filtramos
    if len(tags_a) == 0:
        tags_a = soup.find_all('a', href=True)
    
    for tag in tags_a:
        href = tag['href']
        
        # Filtro flexível: o '/title/tt' só precisa ESTAR no link, não importa onde
        if '/title/tt' in href:
            caminho_limpo = href.split('?')[0] 
            
            # Checa se o link já veio completo do site
            if caminho_limpo.startswith('http'):
                url_completa = caminho_limpo
            else:
                url_completa = f"https://www.imdb.com{caminho_limpo}"
                
            links_filmes.append(url_completa)
            
    # Remove as duplicatas mantendo a ordem do Top 250
    links_filmes = list(dict.fromkeys(links_filmes))[:250]
    
    # LIMITADOR PARA TESTE
    links_para_baixar = links_filmes
    print(f"Encontrados {len(links_filmes)} filmes válidos no HTML! Vamos raspar {len(links_para_baixar)} para teste...\n")
    # ---------------------------------------------------------
    # PASSO 2: ENTRAR EM CADA PÁGINA E EXTRAIR DADOS
    # ---------------------------------------------------------
    for index, url_filme in enumerate(links_para_baixar):
        print(f"[{index+1}/{len(links_para_baixar)}] Raspando: {url_filme}")
        
        navegador.get(url_filme)
        time.sleep(3) # Espera o JS do filme carregar
        
        soup_filme = BeautifulSoup(navegador.page_source, 'html.parser')
        
        # Buscando o JSON-LD escondido no HTML
        json_ld_tag = soup_filme.find('script', type='application/ld+json')
        
        if json_ld_tag:
            try:
                dados_estruturados = json.loads(json_ld_tag.string)
                
                titulo = dados_estruturados.get('name', 'Título não encontrado')
                
                data_pub = dados_estruturados.get('datePublished')
                ano = data_pub.split('-')[0] if data_pub else "Ano não encontrado"
                
                nota = dados_estruturados.get('aggregateRating', {}).get('ratingValue', 'Sem nota')
                
                generos = dados_estruturados.get('genre', [])
                if isinstance(generos, str): 
                    generos = [generos]
                    
                diretores_brutos = dados_estruturados.get('director', [])
                if isinstance(diretores_brutos, dict): 
                    diretores_brutos = [diretores_brutos]
                diretores = [d.get('name') for d in diretores_brutos if d.get('type') == 'Person']
                if not diretores:
                    diretores = ["Diretor não encontrado"]
                    
                url_poster = dados_estruturados.get('image', 'Sem poster')
                caminho_imagem_local = "Sem imagem salva"
                
                if url_poster != 'Sem poster':
                    nome_arquivo_poster = f"poster_{index+1}.jpg"
                    caminho_imagem_local = os.path.join(pasta_posters, nome_arquivo_poster)
                    
                    try:
                        # Para a imagem, a requisição normal costuma funcionar pois é de outro servidor (Amazon)
                        img_data = requests.get(url_poster).content
                        with open(caminho_imagem_local, 'wb') as img_file:
                            img_file.write(img_data)
                    except Exception as e:
                        caminho_imagem_local = "Erro ao baixar imagem"
                
                filme_info = {
                    "titulo": titulo,
                    "ano": ano,
                    "nota_imdb": nota,
                    "generos": generos,
                    "diretores": diretores,
                    "url_poster": url_poster,
                    "imagem_poster_local": caminho_imagem_local
                }
                
                filmes_dados.append(filme_info)
                
            except json.JSONDecodeError:
                print(f"  -> Erro ao ler os dados estruturados do filme.")
        else:
            print(f"  -> Tag JSON-LD não encontrada para este filme.")
            
finally:
    # Sempre fecha o navegador no final, mesmo se der erro
    navegador.quit()
    print("Navegador fechado.")

# ---------------------------------------------------------
# PASSO 3: SALVAR TUDO EM JSON
# ---------------------------------------------------------
if filmes_dados:
    with open('top_filmes_imdb.json', 'w', encoding='utf-8') as f:
        json.dump(filmes_dados, f, ensure_ascii=False, indent=4)
        
    print("\nSUCESSO! Raspagem concluída.")
    print("Verifique o arquivo 'top_filmes_imdb.json' e a pasta 'posters_imdb'.")