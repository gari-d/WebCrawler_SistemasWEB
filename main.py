from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Iniciando a aplicação Flask
app = Flask(__name__)

# Definindo a URL onde estão listadas as ferramentas
URL_PAGINA_FERRAMENTAS = 'https://www.abrafer.com.br/ferramentas-manuais?page={}'

def capturar_dados():
    arquivo_dados = 'dados_ferramentas.csv'
    
    # Remove o arquivo antigo para substituir pelos dados atualizados
    if os.path.exists(arquivo_dados):
        os.remove(arquivo_dados)

    # Lista para armazenar dados das ferramentas
    lista_ferramentas = []

    # Faz um loop para capturar dados de várias páginas
    for numero_pagina in range(1, 14):  
        response = requests.get(URL_PAGINA_FERRAMENTAS.format(numero_pagina))
        response.raise_for_status()
        
        # Analisa o conteúdo da página
        soup = BeautifulSoup(response.text, 'html.parser')
        ferramentas = soup.find_all('div', class_='product-card__info')
        
        # Interrompe o loop se não houver ferramentas
        if not ferramentas:
            break
        
        # Extrai e armazena os dados de cada ferramenta
        for ferramenta in ferramentas:
            codigo = ferramenta.get('data-codigo-produto')
            nome = ferramenta.get('data-nome')
            preco = f'R$ {ferramenta.get("data-preco")}'
            link = ferramenta.find('a').get('href') if ferramenta.find('a') else 'Link não encontrado'
            
            lista_ferramentas.append({
                'Código da ferramenta': codigo,
                'Nome': nome,
                'Preço': preco,
                'Link': link
            })

    # Converte a lista para um DataFrame e salva em CSV
    df = pd.DataFrame(lista_ferramentas)
    df.to_csv(arquivo_dados, index=False, encoding='utf-8')
    print(f'Dados capturados e salvos em {arquivo_dados} às {datetime.now()}')

# Configura o agendamento para atualizar dados diariamente
scheduler = BackgroundScheduler()
scheduler.add_job(func=capturar_dados, trigger="interval", days=1)
scheduler.start()

# Rota para capturar dados manualmente
@app.route('/capturar', methods=['GET'])
def endpoint_capturar():
    try:
        nome_arquivo_csv = capturar_dados()
        return jsonify({
            'message': 'Dados capturados e salvos com sucesso.',
            'arquivo': nome_arquivo_csv
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Executa a aplicação e encerra o scheduler ao fechar
if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        scheduler.shutdown()
