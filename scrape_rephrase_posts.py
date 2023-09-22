import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import random
import spacy

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Load stop words
stop_words = set(stopwords.words('english'))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# URL of the webpage you want to scrape
url = 'https://arynews.tv/putin-discusses-bilateral-ties-brics-with-indias-modi/'

# Headers to mimic a request from a Chrome browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}

# Send a GET request to the webpage
response = requests.get(url, headers=headers)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Target the path with tag names and class names to get title and content
title_tag = soup.find('h1', class_='tdb-title-text')  # Replace with actual tag and class names
content_tag = soup.find('div', class_='single-content')  # Replace with actual tag and class names

# Extract title and content
title = title_tag.text.strip() if title_tag else "Title not found"
content = content_tag.get_text(separator='\n') if content_tag else "Content not found"

# Tokenize content into sentences
sentences = sent_tokenize(content)

# Initialize NLTK's WordNet for synonyms
# synonyms = wordnet.synsets('modify')
synonyms = nltk.corpus.wordnet

# Function to rephrase a word using synonyms from WordNet while avoiding stop words
def rephrase_word(word):
    synsets = wordnet.synsets(word)
    if synsets:
        syn = random.choice(synsets)
        new_word = syn.lemmas()[0].name()
        return new_word.replace("_", " ") if new_word not in stop_words else word
    else:
        return word

# Function to perform advanced sentence transformation using spaCy while avoiding stop words
def advanced_transform(sentence):
    doc = nlp(sentence)
    new_sentence = []

    for token in doc:
        if token.pos_ in ['NOUN', 'VERB'] and rephrase_word(token.text) != token.text:
            new_sentence.append(rephrase_word(token.text))
        else:
            new_sentence.append(token.text)

    return ' '.join(new_sentence)

# Rephrase title using advanced transformation
rephrased_title = advanced_transform(title)

# Rephrase content (excluding quotes and social media content)
modified_paragraphs = []
for paragraph in content.split('\n\n'):  # Assuming paragraphs are separated by double newline
    # Check if the paragraph is a quote or social media content
    if "quote" in paragraph.lower() or "social media" in paragraph.lower():
        modified_paragraphs.append(paragraph)
    else:
        modified_paragraphs.append(advanced_transform(paragraph))

# Generate HTML for WordPress with preserved structure
def generate_html(title, paragraphs):
    non_empty_paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]
    formatted_paragraphs = '\n'.join([f'<p>{paragraph}</p>' for paragraph in non_empty_paragraphs])
    html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <!-- Add SEO meta tags here -->
        </head>
        <body>
            <h1>{title}</h1>
            {formatted_paragraphs}
        </body>
        </html>
    '''
    return html

# Generate HTML code
wordpress_html = generate_html(rephrased_title, modified_paragraphs)

# Print the generated WordPress HTML code
print(wordpress_html)