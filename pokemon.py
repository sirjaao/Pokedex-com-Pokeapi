from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def pegar_dados_pokemon(nome):
    pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{nome.lower()}'
    species_url = f'https://pokeapi.co/api/v2/pokemon-species/{nome.lower()}'
    encounters_url = f'https://pokeapi.co/api/v2/pokemon/{nome.lower()}/encounters'
    
    try:
        poke_res = requests.get(pokemon_url)
        if poke_res.status_code != 200:
            return None
        poke_data = poke_res.json()
        
        species_res = requests.get(species_url)
        if species_res.status_code != 200:
            return None
        species_data = species_res.json()

        encounters_res = requests.get(encounters_url)
        if encounters_res.status_code != 200:
            return None
        encounters_data = encounters_res.json()

        # Obtém a URL da cadeia evolutiva
        evolution_chain_url = species_data['evolution_chain']['url']
        evolution_chain_res = requests.get(evolution_chain_url)
        if evolution_chain_res.status_code != 200:
            return None
        evolution_chain_data = evolution_chain_res.json()

        # Processa as evoluções
        evolucoes = []
        current_evolution = evolution_chain_data['chain']
        while current_evolution:
            evolucoes.append(current_evolution['species']['name'])
            if 'evolves_to' in current_evolution and len(current_evolution['evolves_to']) > 0:
                current_evolution = current_evolution['evolves_to'][0]
            else:
                break

        pokemon_info = {
            "nome": poke_data['name'].capitalize(),
            "tipos": [t['type']['name'] for t in poke_data['types']],
            "altura": poke_data['height'] / 10,  # Convertido para metros
            "peso": poke_data['weight'] / 10,    # Convertido para quilogramas
            "habilidades": [h['ability']['name'] for h in poke_data['abilities']],
            "imagem": poke_data['sprites']['front_default'],  # URL da imagem do Pokémon
            "movimentos": [m['move']['name'] for m in poke_data['moves']],
            "descricao": None,
            "locais": [],
            "evolucoes": evolucoes
        }

        descricao = None
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'pt-BR':
                descricao = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                break
        
        if not descricao:
            for entry in species_data['flavor_text_entries']:
                if entry['language']['name'] == 'en':
                    descricao = entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                    break
        
        pokemon_info["descricao"] = descricao if descricao else "Descrição não disponível."

        locais = [location['location_area']['name'].replace('-', ' ').capitalize() for location in encounters_data]
        pokemon_info["locais"] = locais if locais else ["Nenhuma localização disponível."]
        
        return pokemon_info
    except Exception as e:
        print(e)
        return None
    
def get_pokemon_list():
    url = 'https://pokeapi.co/api/v2/pokemon?limit=1000'  # Ajuste o limite conforme necessário
    response = requests.get(url)
    data = response.json()
    pokemon_list = [pokemon['name'] for pokemon in data['results']]
    return pokemon_list

@app.route('/', methods=['GET', 'POST'])
def index():
    pokemon_list = get_pokemon_list()
    pokemon = None
    if request.method == 'POST':
        pokemon_name = request.form.get('nome')
        if pokemon_name:
            pokemon = pegar_dados_pokemon(pokemon_name)
    return render_template('pokedex.html', pokemon_list=pokemon_list, pokemon=pokemon)

if __name__ == '__main__':
    app.run(debug=True)
