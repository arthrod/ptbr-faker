from security import safe_requests

url = "https://www.cepaberto.com/downloads.csv?name=AC&part=1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = safe_requests.get(url, allow_redirects=True, headers=headers)
print(f"URL: {url}")
print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

if response.status_code == 200:
    with open("AC_part1.zip", "wb") as f:
        f.write(response.content)
    print("File downloaded successfully")
else:
    print("Failed to download file")
    print("Response content:", response.text[:500])
