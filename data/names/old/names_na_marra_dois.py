import json
import logging
from datetime import datetime
from itertools import product
from pathlib import Path
from random import uniform
from string import ascii_uppercase
from time import sleep
from security import safe_requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(f'names_collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'), logging.StreamHandler()],
)


class NameCollector:
    def __init__(self, tokens):
        self.base_url = 'https://portaldatransparencia.gov.br/pessoa-fisica/busca/resultado'
        self.tokens = tokens
        self.output_file = Path('names.jsonl')
        self.batch_size = 100
        self.current_batch = []

    def save_batch(self):
        if not self.current_batch:
            return

        with self.output_file.open('a', encoding='utf-8') as f:
            for record in self.current_batch:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        self.current_batch = []

    def get_names(self, prefix):
        params = {'termo': prefix, 'tamanhoPagina': 100, **self.tokens}

        headers = {
            'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0',
            'Accept': 'application/json',
            'Referer': 'https://portaldatransparencia.gov.br',
        }

        page = 1
        while True:
            params['pagina'] = page
            response = safe_requests.get(self.base_url, params=params, headers=headers)

            if response.status_code == 403:
                logging.error(f'Authentication error for prefix {prefix}. Need new tokens!')
                return False

            if response.status_code != 200:
                logging.error(f'Error {response.status_code} for {prefix} page {page}')
                return True

            data = response.json()
            records = data.get('registros', [])

            if not records:
                break

            for record in records:
                record['prefix'] = prefix
                record['data_coleta'] = datetime.now().isoformat()
                self.current_batch.append(record)

                if len(self.current_batch) >= self.batch_size:
                    self.save_batch()

            logging.info(f'Prefix {prefix} - Page {page}: {len(records)} records')

            if len(records) < 100:
                break

            page += 1
            sleep(uniform(0.1, 1))

        self.save_batch()  # Save any remaining records
        return True


def generate_prefixes(length):
    return [''.join(p) for p in product(ascii_uppercase, repeat=length)]


def main():
    tokens = {
        't': '6BB5rxQk9JYFRDl4hmPt',  # Update this
        'tokenRecaptcha': '03AFcWeA6DpUrky2Te8Zq1cA76dcNeHy0M6FFmAYo1i...',  # Update this
    }

    collector = NameCollector(tokens)
    prefixes_3 = generate_prefixes(3)
    large_prefixes = []

    # Process 3-letter prefixes
    for prefix in prefixes_3:
        logging.info(f'Processing prefix: {prefix}')

        response = safe_requests.get(
            collector.base_url, params={'termo': prefix, 'pagina': 1, 'tamanhoPagina': 1, **tokens}, headers={'User-Agent': 'Mozilla/5.0'}
        )

        if response.status_code == 403:
            logging.error('Authentication error! Need new tokens!')
            return

        total = response.json().get('totalRegistros', 0)

        if total >= 10000:
            large_prefixes.append(prefix)
            continue

        if not collector.get_names(prefix):
            return

        sleep(uniform(0.1, 1))

    # Process 4-letter prefixes for large blocks
    for prefix in large_prefixes:
        for fourth_letter in ascii_uppercase:
            extended_prefix = prefix + fourth_letter
            logging.info(f'Processing extended prefix: {extended_prefix}')

            if not collector.get_names(extended_prefix):
                return

            sleep(uniform(0.1, 1))


if __name__ == '__main__':
    main()
