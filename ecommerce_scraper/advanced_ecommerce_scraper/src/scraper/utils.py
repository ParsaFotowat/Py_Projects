def clean_text(text):
    return ' '.join(text.split()).strip()

def handle_request(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < retries - 1:
                continue
            else:
                raise e

def delay_request(seconds):
    time.sleep(seconds)