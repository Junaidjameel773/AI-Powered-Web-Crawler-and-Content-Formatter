import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import asyncio
from crawl4ai import AsyncWebCrawler
import os
from dotenv import load_dotenv


def extract_all_urls(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch the webpage")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []

    for a_tag in soup.find_all('a', href=True):  # Find all <a> tags with href attributes
        link = a_tag['href']
        
        # Convert relative URLs to absolute URLs
        if not link.startswith("http"):
            link = requests.compat.urljoin(url, link)
        links.append(link)
    return links

## Naming text file according to the URL
def url_to_filename(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname  # e.g., 'www.nadra.gov.pk'
    
    if hostname:
        parts = hostname.split('.')
        # Handle cases like www.nadra.gov.pk or dgip.gov.pk
        if len(parts) >= 3:
            domain = parts[-3]  # gets 'nadra' from 'www.nadra.gov.pk'
        else:
            domain = parts[0]   # fallback to the first part
        return f"{domain}.txt"
    else:
        raise ValueError("Invalid URL")


main_url = input("Enter website to crawl: ")
links = extract_all_urls(main_url)

def filter_links_by_main_domain(links, main_url):
    # Extract main keyword from main_url
    parsed_main = urlparse(main_url)
    domain_parts = parsed_main.netloc.split('.')
    if len(domain_parts) < 2:
        return []  # invalid main_url

    main_keyword = domain_parts[-2].lower()  # e.g., 'nadra' from 'www.nadra.gov.pk'

    filtered_links = []
    for link in links:
        try:
            parsed = urlparse(link)
            domain = parsed.netloc.lower()
            parts = domain.split('.')
            for part in parts:
                if main_keyword in part:
                    filtered_links.append(link)
                    break
        except Exception:
            continue  # ignore malformed links
    return filtered_links
def remove_duplicate_urls(filt_list):
    seen = set()
    unique_urls = []
    for url in filt_list:
        if url not in seen:
            unique_urls.append(url)
            seen.add(url)
    return unique_urls

filt_links = filter_links_by_main_domain(links, main_url)
filt_links  = remove_duplicate_urls(filt_links)
file_name = url_to_filename(main_url)


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Gemini endpoint and headers
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
HEADERS = {"Content-Type": "application/json"}

# Gemini prompt template
def make_prompt(input_text):
    return f"""
You are a helpful assistant. Take the input text and convert it into clean, structured Markdown format.

Input:
\"\"\"
{input_text}
\"\"\"

Output only the Markdown version, no explanations.
"""

# Function to call Gemini API
def generate_markdown(text):
    prompt = make_prompt(text)
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_URL, headers=HEADERS, json=data)

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        print("Error from Gemini:", response.status_code)
        print(response.text)
        return ""

# Async function to process all links
async def process_links(links):
    async with AsyncWebCrawler() as crawler:
        for link in links:
            print(f"Processing: {link}")
            try:
                result = await crawler.arun(url=link)
                raw_markdown = result.markdown
                clean_markdown = generate_markdown(raw_markdown)

                # Append result to file
                with open(file_name, "a", encoding="utf-8") as f:
                    f.write(f"\n\n--- Content from: {link} ---\n\n")
                    f.write(clean_markdown)
                    f.write("\n\n")
                print(f"✓ Saved content from {link}\n")
            except Exception as e:
                print(f"Failed to process {link}: {e}")

# Run the async job
asyncio.run(process_links(filt_links))


