import os
import requests
from typing import Dict, List
import time

# State data with abbreviations and total records
STATE_DATA = {
    'AC': ('Acre', 4102),
    'AL': ('Alagoas', 11106),
    'AM': ('Amazonas', 16452),
    'AP': ('Amapá', 2802),
    'BA': ('Bahia', 58251),
    'CE': ('Ceara', 32333),
    'DF': ('Distrito Federal', 36285),
    'ES': ('Espirito Santo', 32401),
    'GO': ('Goiás', 65251),
    'MA': ('Maranhão', 15491),
    'MG': ('Minas Gerais', 116184),
    'MS': ('Mato Grosso do Sul', 14879),
    'MT': ('Mato Grosso', 19847),
    'PA': ('Pará', 24946),
    'PB': ('Paraíba', 14236),
    'PE': ('Pernambuco', 50527),
    'PI': ('Piauí', 13388),
    'PR': ('Paraná', 59562),
    'RJ': ('Rio de Janeiro', 99422),
    'RN': ('Rio Grande do Norte', 15415),
    'RO': ('Rondônia', 11217),
    'RR': ('Roraima', 2620),
    'RS': ('Rio Grande do Sul', 58396),
    'SC': ('Santa Catarina', 46548),
    'SE': ('Sergipe', 6131),
    'SP': ('São Paulo', 300850),
    'TO': ('Tocantins', 8554),
}

def download_state_part(state_abbrev: str, part: int, output_dir: str) -> bool:
    """
    Download a specific part of a state's data.
    
    Args:
        state_abbrev: Two-letter state abbreviation
        part: Part number (1-5)
        output_dir: Directory to save the downloaded file
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    url = f"https://www.cepaberto.com/downloads.csv?name={state_abbrev}&part={part}"
    output_file = os.path.join(output_dir, f"{state_abbrev}_part{part}.zip")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, allow_redirects=True, headers=headers, timeout=60)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded {output_file}")
            return True
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def main():
    # Create output directory
    output_dir = "state_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Download all parts for all states
    for state_abbrev, (state_name, total_records) in STATE_DATA.items():
        print(f"\nProcessing {state_name} ({state_abbrev}) - Total records: {total_records}")
        
        for part in range(1, 6):  # Parts 1-5
            success = download_state_part(state_abbrev, part, output_dir)
            if not success:
                print(f"Failed to download part {part} for {state_name}")
            time.sleep(1)  # Add a small delay between downloads to be nice to the server

if __name__ == "__main__":
    main()
