import json
from datetime import datetime
from pathlib import Path
from string import ascii_uppercase
from time import sleep

import requests
import typer
import secrets


def get_names_by_letter(letter, last_page=None):
    base_url = 'https://portaldatransparencia.gov.br/pessoa-fisica/busca/resultado'
    page = 1
    page_size = 100

    headers = {
        'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0',
        'Accept': 'application/json',
        'Referer': 'https://portaldatransparencia.gov.br',
    }

    params = {
        'letraInicial': letter,
        'tamanhoPagina': page_size,
        't': '6BB5rxQk9JYFRDl4hmPt',  # Update this token
        'tokenRecaptcha': '03AFcWeA6DpUrky2Te8Zq1cA76dcNeHy0M6FFmAYo1i...',  # Update this token
    }

    output_file = Path('names.jsonl')

    while True:
        if last_page and page > last_page:
            break

        params['pagina'] = page
        response = requests.get(base_url, params=params, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f'Error on letter {letter} page {page}: {response.status_code}')
            break

        data = response.json()
        records = data.get('registros', [])

        if not records:
            break

        with output_file.open('a', encoding='utf-8') as f:
            for record in records:
                record['letra'] = letter
                record['data_coleta'] = datetime.now().isoformat()
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        print(f'Letter {letter} - Page {page}: {len(records)} records')

        if len(records) < page_size:
            break

        page += 1
        sleep(secrets.SystemRandom().uniform(0.1, 1))


def main(
    custom_start: str = typer.Option(
        None,
        '--start-letter',
        '-s',
        help='Start processing from this letter (A-Z)',
    ),
):
    start_idx = 0
    if custom_start:
        custom_start = custom_start.upper()
        if custom_start not in ascii_uppercase:
            typer.echo(f'Error: Start letter must be A-Z, got {custom_start}')
            raise typer.Exit(1)
        start_idx = ascii_uppercase.index(custom_start)

    for letter in ascii_uppercase[start_idx:]:
        print(f'\nProcessing letter {letter}')
        get_names_by_letter(letter)
        sleep(secrets.SystemRandom().uniform(1, 3))


if __name__ == '__main__':
    typer.run(main)
