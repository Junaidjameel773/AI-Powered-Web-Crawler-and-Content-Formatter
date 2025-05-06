# 🌐 Website Content Crawler & Cleaner (Markdown Converter)

This Python script crawls a given website, extracts internal links, fetches content from those links, and converts the extracted text into clean, structured **Markdown** using **Google Gemini API**.

---

## 🚀 Features

- ✅ Extracts and filters all internal links from a given website
- ✅ Removes duplicate URLs
- ✅ Uses `crawl4ai` for asynchronous web crawling
- ✅ Sends raw content to **Gemini API** for formatting into clean Markdown
- ✅ Saves output into a `.txt` file named after the domain (e.g., `nadra.txt`)

---

## 📦 Requirements

Install dependencies with:

```bash
pip install -r requirements.txt

```
Create a .env file in your project root and add your Google Gemini API key:
``` cmd
GOOGLE_API_KEY=your_gemini_api_key_here
