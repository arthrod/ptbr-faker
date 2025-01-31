def fix_city_names():
    corrections = {
        'Ererê_CE': 'Ereré',
        'Fortaleza do Tabocão_TO': 'Tabocão',
        'Muquém de São Francisco_BA': 'Muquém do São Francisco',
        'Dona Eusébia_MG': 'Dona Euzébia',
        'Grão Pará_SC': 'Grão-Pará',
        'São Thomé das Letras_MG': 'São Tomé das Letras',
        'Itaóca_SP': 'Itaoca',
        'Biritiba-Mirim_SP': 'Biritiba Mirim',
        'Passa-Vinte_MG': 'Passa Vinte',
        'Boa Saúde_RN': 'Januário Cicco',
        'Atílio Vivacqua_ES': 'Atílio Vivácqua',
        'Iuiú_BA': 'Iuiu',
        'Santa Teresinha_BA': 'Santa Terezinha',
        'Amparo de São Francisco_SE': 'Amparo do São Francisco',
    }

    import json

    # Read the file
    with open('cities_with_ceps.jsonl', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove empty lines and whitespace

    # Process each line
    corrected_lines = []
    for i, line in enumerate(lines, 1):
        try:
            city_data = json.loads(line)
            city_key = next(iter(city_data))  # Get the city key

            if city_key in corrections:
                city_data[city_key]['city_name'] = corrections[city_key]

            corrected_lines.append(json.dumps(city_data, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f'Error in line {i}:')
            print(f'Line content: {line}')
            print(f'Error message: {e!s}')
            raise  # Re-raise the exception after printing debug info

    # Write back to file
    with open('cities_with_ceps.jsonl', 'w', encoding='utf-8') as f:
        for line in corrected_lines:
            f.write(line + '\n')


if __name__ == '__main__':
    fix_city_names()
