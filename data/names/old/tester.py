import marimo

__generated_with = '0.10.15'
app = marimo.App()


@app.cell
def _():
    import time
    from random import randint

    import requests

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
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
        'Accept': 'application/json',
        'Origin': 'https://transparencia.registrocivil.org.br',
        'Referer': 'https://transparencia.registrocivil.org.br/',
    }
    import json

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
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
        'Accept': 'application/json',
        'Origin': 'https://transparencia.registrocivil.org.br',
        'Referer': 'https://transparencia.registrocivil.org.br/',
    }

    def get_state_data(state):
        url = f'https://transparencia.registrocivil.org.br/api/record/all-name?start_date=2010-01-01&end_date=2010-12-31&translate=1&state={state}'

        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f'\n=== {state} ===')
            print(json.dumps(data, indent=2))
        else:
            print(f'{state}: Error {response.status_code}')
        time.sleep(randint(1, 3))

    for state in ESTADOS:
        get_state_data(state)
    return (
        ESTADOS,
        HEADERS,
        get_state_data,
        json,
        randint,
        requests,
        state,
        time,
    )


if __name__ == '__main__':
    app.run()
