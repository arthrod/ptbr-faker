import json
import time
from urllib.parse import parse_qs, urlparse

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver  # This gives access to requests


def get_new_token():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get('https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista')
        time.sleep(3)  # Wait for page load

        for request in driver.requests:
            if 'resultado' in request.url:
                url_params = dict(parse_qs(urlparse(request.url).query))
                t_token = url_params.get('t', [None])[0]
                recaptcha = url_params.get('tokenRecaptcha', [None])[0]
                if t_token and recaptcha:
                    return t_token, recaptcha

    finally:
        driver.quit()

    return None, None


# Get tokens and make request
t_token, recaptcha = get_new_token()
if t_token and recaptcha:
    params = {'letraInicial': 'A', 'pagina': 1, 'tamanhoPagina': 100, 't': t_token, 'tokenRecaptcha': recaptcha}
    response = requests.get('https://portaldatransparencia.gov.br/pessoa-fisica/busca/resultado', params=params)
    print(json.dumps(response.json(), indent=2))
