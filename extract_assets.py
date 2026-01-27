import json
import re
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_DIR = r"C:\Users\jmfs2\.gemini\antigravity\scratch\utagawa-kogyo"
HTML_FILE = os.path.join(BASE_DIR, "utagawa_source.html")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
TEXT_OUTPUT = os.path.join(BASE_DIR, "extracted_content.txt")

os.makedirs(ASSETS_DIR, exist_ok=True)

def download_image(url, save_dir):
    try:
        filename = url.split('/')[-1]
        # Clean filename
        filename = re.sub(r'[^\w\-.]', '_', filename)
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
            filename += ".jpg" # Default extension if missing
            
        save_path = os.path.join(save_dir, filename)
        
        if os.path.exists(save_path):
            return filename

        print(f"Downloading: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return filename
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def extract_from_nuxt_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    script = soup.find('script', {'id': '__NUXT_DATA__'})
    
    images = set()
    texts = []

    if script:
        try:
            data = json.loads(script.string)
            # Recursively search for strings that look like URLs or Japanese text
            def recursive_search(item):
                if isinstance(item, str):
                    if item.startswith('http') and ('storage.googleapis.com' in item or 'images' in item):
                        images.add(item)
                    elif len(item) > 2 and re.search(r'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]', item): # Check for Japanese characters
                        texts.append(item)
                elif isinstance(item, list):
                    for sub in item:
                        recursive_search(sub)
                elif isinstance(item, dict):
                    for sub in item.values():
                        recursive_search(sub)
            
            recursive_search(data)
        except json.JSONDecodeError:
            print("Failed to parse NUXT data")

    return list(images), texts

def main():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    images, texts = extract_from_nuxt_data(content)

    print(f"Found {len(images)} images.")
    print(f"Found {len(texts)} text segments.")

    # Download images
    downloaded_map = {}
    for img_url in images:
        local_name = download_image(img_url, ASSETS_DIR)
        if local_name:
            downloaded_map[img_url] = local_name

    # Save texts
    with open(TEXT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write("\n".join(texts))
    
    print("Extraction complete.")

if __name__ == "__main__":
    main()
