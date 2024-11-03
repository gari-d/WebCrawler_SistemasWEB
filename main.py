from flask import Flask
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Iniciando a aplicação Flask
app = Flask(__name__)

# Aqui é onde definimos a URL que contem nossas ferramentas:
url = 'https://www.abrafer.com.br/ferramentas-manuais?page={}'

def capturar_dados():
    arquivo_dados = 'dados_ferramentas.csv'
    
    # Verifica se o arquivo existe, se sim, carrega o arquivo, se não, cria um DataFrame vazio
    if os.path.exists(arquivo_dados):
        os.remove(arquivo_dados)

    # Cria um dataframe que vai receber os dados das ferramentas    
    todas_ferramentas = []

    # Aqui fazemos o loop para capturar os dados de todas as páginas (podemos mudar a quantidade de páginas)
    for page in range(1, 14):  
        response = requests.get(url.format(page))
        response.raise_for_status()
        
        # Aqui é onde utilizamos o BeautifulSoup para capturar os dados da página (Com os dados que identificamos na paginas web utilizando o inspecionar elemento)
        soup = BeautifulSoup(response.text, 'html.parser')
        ferramentas = soup.find_all('div', class_='product-card__info')
        
        # Se não houver ferramentas, saia do loop
        if not ferramentas:
            break
        
        # Aqui é onde verificamos todos as ferramentas e salvamos no arquivo csv (Precisa implementar a verificação se a ferramenta ja foi salva)
        for ferramenta in ferramentas:
            codigo_ferramenta = ferramenta.get('data-codigo-produto')
            nome = ferramenta.get('data-nome')
            preco = f'R$ {ferramenta.get("data-preco")}'
            link = ferramenta.find('a').get('href') if ferramenta.find('a') else 'Link não encontrado'
            
            # Adiciona os dados ao dicionário de todas_ferramentas
            todas_ferramentas.append({
                'Código da ferramenta': codigo_ferramenta,
                'Nome': nome,
                'Preço': preco,
                'Link': link
            })
        print("Nenhuma ferramenta nova encontrada.")
# Aqui é a rota da aplicação (precisamos definir o metodo get que ira capturar as feramentas e utilizar as funções).
@app.route('/capturar', methods=['GET'])
def endpoint_capturar():
    return "Endpoint de captura da aplicação"

if __name__ == '__main__':
    app.run(debug=True)