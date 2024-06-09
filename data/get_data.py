import json
import os

import requests


def get_wikipedia_content(title):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
    }
    response = requests.get(url, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    return page["title"], page["extract"]


def get_wikipedia_title(url):
    # Extract the title from a Wikipedia URL
    return url.split("/wiki/")[1]


def extract_text_from_urls(urls):
    data = []
    for url in urls:
        title = get_wikipedia_title(url)
        page_title, content = get_wikipedia_content(title)
        data.append({"title": page_title, "url": url, "content": content})
        print(f"Extracted content from {url}")
    return data


def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# Example list of Wikipedia URLs
urls = [
    "https://en.wikipedia.org/wiki/Genghis_Khan",
    "https://en.wikipedia.org/wiki/Mongol_Empire",
    "https://en.wikipedia.org/wiki/Khan_(title)",
    "https://en.wikipedia.org/wiki/Yesugei",
    "https://en.wikipedia.org/wiki/Naimans",
]

# Extract text content from the URLs
extracted_data = extract_text_from_urls(urls)

# Save the extracted data to a JSON file
json_filename = "./data/wikipedia_content.json"
save_to_json(extracted_data, json_filename)

print(f"Saved extracted data to {json_filename}")
