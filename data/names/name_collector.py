import csv
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from random import randint
from zoneinfo import ZoneInfo  # Modern timezone handling

import requests

# Configure logging with timezone-aware timestamps
logging_filename = Path(f'name_collection_{datetime.now(tz=ZoneInfo("UTC")).strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(logging_filename), logging.StreamHandler(sys.stdout)],
)

# Constants
ESTADOS = [
    'AC',
    'AL',
    'AP',
    'AM',
    'BA',
    'CE',
    'DF',
    'ES',
    'GO',
    'MA',
    'MT',
    'MS',
    'MG',
    'PA',
    'PB',
    'PR',
    'PE',
    'PI',
    'RJ',
    'RN',
    'RS',
    'RO',
    'RR',
    'SC',
    'SP',
    'SE',
    'TO',
]
ANOS = list(range(2024, 2009, -1))  # 2024 to 2010
BATCH_SIZE = 100
BASE_URL = 'https://transparencia.registrocivil.org.br/api/record/all-name'

# Browser-like headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://transparencia.registrocivil.org.br',
    'Referer': 'https://transparencia.registrocivil.org.br/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


class NameDataCollector:
    def __init__(self):
        self.names_by_state = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.names_total = defaultdict(lambda: defaultdict(int))
        self.processed_names = set()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def make_api_request(self, year, state):
        """Make API request with enhanced error handling and retry logic"""
        max_retries = 5
        retry_delays = [5, 10, 15, 30, 60]

        for attempt, delay in enumerate(retry_delays[:max_retries]):
            try:
                url = f'{BASE_URL}?start_date={year}-01-01&end_date={year}-12-31&translate=1&state={state}'
                time.sleep(randint(0, 15))

                response = self.session.get(url, timeout=30)

                if response.status_code == 403:
                    logging.error(f'Access forbidden for {state}-{year}. Response: {response.text}')
                    time.sleep(randint(30, 60))
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logging.warning(f'Timeout for {state}-{year} (Attempt {attempt + 1}/{max_retries})')
            except requests.exceptions.RequestException as e:
                logging.exception(f'Request error for {state}-{year}: {e!s} (Attempt {attempt + 1}/{max_retries})')
                if hasattr(e, 'response') and e.response is not None:
                    logging.exception(f'Response text: {e.response.text}')
            except json.JSONDecodeError as e:
                logging.exception(f'JSON decode error for {state}-{year}: {e!s}')

            if attempt < max_retries - 1:
                wait_time = delay + randint(0, 5)
                logging.info(f'Waiting {wait_time} seconds before retry...')
                time.sleep(wait_time)

        logging.error(f'Failed to fetch data for {state}-{year} after {max_retries} attempts')
        return {'status': 0, 'data': []}

    def process_response(self, response, year, state):
        """Process API response while preserving complete names and ensuring type safety"""
        if not isinstance(response, dict) or response.get('status') != 1 or 'data' not in response:
            return

        for item in response['data']:
            try:
                name = str(item['name']).strip()
                # Ensure total is converted to integer
                total = int(item['total'])

                # Update state-specific data
                self.names_by_state[year][name][state] = total

                # Update historical totals
                self.names_total[name][year] = self.names_total[name][year] + total

                # Track processed names
                self.processed_names.add(name)

                # Save batch if threshold reached
                if len(self.processed_names) % BATCH_SIZE == 0:
                    self.save_data()
                    logging.info(f'Processed {len(self.processed_names)} unique names so far...')

            except (KeyError, ValueError, TypeError) as e:
                logging.exception(f'Error processing item {item}: {e!s}')
                continue

    def save_state_data(self, year):
        """Save state-specific data using pathlib and modern Python idioms"""
        filename = Path(f'names_by_state_{year}.csv')

        try:
            with filename.open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Modern list concatenation
                writer.writerow(['Nome', *ESTADOS])

                # Use list comprehension for row construction
                for name in sorted(self.names_by_state[year].keys()):
                    row = [name]
                    row.extend(self.names_by_state[year][name].get(state, 0) for state in ESTADOS)
                    writer.writerow(row)

            logging.info(f'Successfully saved state data for {year}')
        except Exception as e:
            logging.exception(f'Error saving state data for {year}: {e!s}')

    def save_historical_data(self):
        """Save historical totals using pathlib"""
        filename = Path('names_historical_totals.csv')

        try:
            with filename.open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Nome', *[str(year) for year in ANOS]])

                for name in sorted(self.names_total.keys()):
                    row = [name]
                    row.extend(self.names_total[name].get(year, 0) for year in ANOS)
                    writer.writerow(row)

            logging.info('Successfully saved historical totals')
        except Exception as e:
            logging.exception(f'Error saving historical totals: {e!s}')

    def save_data(self):
        """Save all current data with progress tracking"""
        logging.info(f'Saving batch of {len(self.processed_names)} unique names...')
        for year in ANOS:
            self.save_state_data(year)
        self.save_historical_data()

    def collect_data(self):
        """Main data collection process with enhanced progress tracking"""
        total_combinations = len(ANOS) * len(ESTADOS)
        processed = 0

        try:
            for year in ANOS:
                logging.info(f'\nProcessing year {year}')
                for state in ESTADOS:
                    processed += 1
                    progress = (processed / total_combinations) * 100
                    logging.info(f'Processing {state} for {year} ({progress:.1f}% complete)')

                    response = self.make_api_request(year, state)
                    self.process_response(response, year, state)

                    delay = randint(2, 5)
                    logging.debug(f'Waiting {delay} seconds before next request...')
                    time.sleep(delay)

                self.save_data()
                logging.info(f'Completed processing for year {year}')

        except KeyboardInterrupt:
            logging.warning('\nProcess interrupted by user. Saving current progress...')
            self.save_data()
            raise
        except Exception as e:
            logging.exception(f'Unexpected error: {e!s}')
            self.save_data()
            raise


def main():
    logging.info('Starting name data collection')
    logging.info(f'Processing years: {ANOS[0]} to {ANOS[-1]}')
    logging.info(f"Processing states: {', '.join(ESTADOS)}")

    try:
        collector = NameDataCollector()
        collector.collect_data()
        logging.info('Data collection completed successfully')
    except KeyboardInterrupt:
        logging.info('Process terminated by user')
        sys.exit(1)
    except Exception as e:
        logging.exception(f'Process failed: {e!s}')
        sys.exit(1)


if __name__ == '__main__':
    main()
