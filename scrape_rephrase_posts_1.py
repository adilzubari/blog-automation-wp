import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize
from paraphrase import Paraphraser

# Download the 'punkt' resource from NLTK
nltk.download('punkt')

# URL of the webpage you want to scrape
url = 'https://example.com/blog'

# Headers to mimic a request from a Chrome browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}

# Send a GET request to the webpage
response = requests.get(url, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Target the path with tag names and class names to get title and content
title_tag = soup.find('h1', class_='blog-title')  # Replace with actual tag and class names
content_tag = soup.find('div', class_='blog-content')  # Replace with actual tag and class names

# Extract title and content
title = title_tag.text.strip() if title_tag else "Title not found"
content = content_tag.get_text(separator='\n') if content_tag else "Content not found"

# Initialize the paraphraser
paraphraser = Paraphraser()

# Rephrase title and content
rephrased_title = paraphraser.paraphrase(title)[0]['paraphrase']
rephrased_content = '\n'.join([paraphraser.paraphrase(sentence)[0]['paraphrase'] for sentence in sent_tokenize(content)])

# Generate HTML for WordPress with preserved structure
def generate_html(title, content):
    html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <!-- Add SEO meta tags here -->
        </head>
        <body>
            <h1>{title}</h1>
            {content}
        </body>
        </html>
    '''
    return html

# Wrap paragraphs in <p> tags
rephrased_content = '\n'.join(f'<p>{paragraph}</p>' for paragraph in rephrased_content.split('\n'))

# Generate HTML code
wordpress_html = generate_html(rephrased_title, rephrased_content)

# Print the generated WordPress HTML code
print(wordpress_html)
