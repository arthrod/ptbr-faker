import json

import jsonlines


def load_data():
    with open('population_data_2024_complete.json', encoding='utf-8') as f:
        return json.load(f)


def create_spelling_map():
    # Map of different spellings with comments
    return {
        'Ereré_CE': ('Ererê_CE', 'City also known as Ereré'),
        'Tabocão_TO': ('Fortaleza do Tabocão_TO', 'City also known as Tabocão'),
        'Muquém do São Francisco_BA': ('Muquém de São Francisco_BA', 'City also known as Muquém do São Francisco'),
        'Dona Euzébia_MG': ('Dona Eusébia_MG', 'City also known as Dona Euzébia'),
        'Grão-Pará_SC': ('Grão Pará_SC', 'City also known as Grão-Pará'),
        'São Tomé das Letras_MG': ('São Thomé das Letras_MG', 'City also known as São Tomé das Letras'),
        'Itaoca_SP': ('Itaóca_SP', 'City also known as Itaoca'),
        'Biritiba Mirim_SP': ('Biritiba-Mirim_SP', 'City also known as Biritiba Mirim'),
        'Passa Vinte_MG': ('Passa-Vinte_MG', 'City also known as Passa Vinte'),
        'Januário Cicco_RN': ('Boa Saúde_RN', 'City also known as Januário Cicco'),
        'Atílio Vivácqua_ES': ('Atílio Vivacqua_ES', 'City also known as Atílio Vivácqua'),
        'Iuiu_BA': ('Iuiú_BA', 'City also known as Iuiu'),
        'Santa Terezinha_BA': ('Santa Teresinha_BA', 'City also known as Santa Terezinha'),
        "Olho d'Água do Borges_RN": ("Olho-d'Água do Borges_RN", "City also known as Olho d'Água do Borges"),
        'Amparo do São Francisco_SE': ('Amparo de São Francisco_SE', 'City also known as Amparo do São Francisco'),
    }


def merge_city_data():
    population_data = load_data()
    spelling_map = create_spelling_map()

    # Read the missing cities file
    missing_cities = {}
    with jsonlines.open('missing_cities.jsonl', 'r') as reader:
        for item in reader:
            city_key = f"{item['city_name']}_{item['state']}"
            missing_cities[city_key] = item

    # Process and merge the data
    revised_missing = []

    for pop_spelling, (code_spelling, comment) in spelling_map.items():
        pop_city_data = population_data['cities'].get(pop_spelling)
        code_city_data = missing_cities.get(code_spelling)

        if pop_city_data and code_city_data:
            # Merge the data and add the comment
            pop_city_data.update(
                {
                    'ddd': code_city_data['ddd'],
                    'cep_range_begins': code_city_data['cep_range_begins'],
                    'cep_range_ends': code_city_data['cep_range_ends'],
                    'cep_range_begins_two': code_city_data['cep_range_begins_two'],
                    'cep_range_ends_two': code_city_data['cep_range_ends_two'],
                    'ibge_code': code_city_data['ibge_code'],
                    'comment': comment,
                }
            )

            # Remove from population data under old key and add under standardized key
            if pop_spelling != code_spelling:
                population_data['cities'][code_spelling] = pop_city_data
                del population_data['cities'][pop_spelling]
        else:
            # If we couldn't match and merge, add to revised missing cities
            revised_missing.append(
                {
                    'source': 'unmatched',
                    'population_spelling': pop_spelling,
                    'code_spelling': code_spelling,
                    'population_data': pop_city_data,
                    'code_data': code_city_data,
                }
            )

    # Save updated population data
    with open('population_data_2024_complete_revised.json', 'w', encoding='utf-8') as f:
        json.dump(population_data, f, ensure_ascii=False, indent=2)

    # Save any remaining unmatched cities
    with jsonlines.open('missing_cities_revised.jsonl', 'w') as writer:
        for item in revised_missing:
            writer.write(item)


if __name__ == '__main__':
    try:
        merge_city_data()
        print('City data merge and spelling fixes completed successfully')
    except Exception as e:
        print(f'An error occurred during city data merge: {e}')
