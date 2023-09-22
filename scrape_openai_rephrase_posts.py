import requests
from bs4 import BeautifulSoup
import pyperclip

# Number of posts to fetch from database
postsToFetch = 1

# Hasura server URL
hasura_url = "https://nexus-logix.hasura.app/v1/graphql"

# Admin secret for authentication
admin_secret = "g7nPwES1QWyhT1HLAJnWvvGGWx6ZjzhmT1gYKP2h6eVjf0vaWvuVKHnMi9UZTc3U"

# GraphQL query to fetch records
graphql_query = """
{
  gt_scrape_posts(limit: """ + str(postsToFetch) + """, where: {scraped: {_eq: false}}) {
    id
    url
    scraped
  }
}
"""

# Prepare GraphQL headers for the request
graphql_headers = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": admin_secret
}

# Create the request payload
payload = {
    "query": graphql_query
}

# Send the GraphQL request to the Hasura server
graphql_response = requests.post(hasura_url, json=payload, headers=graphql_headers)

# Parse the JSON response
data = graphql_response.json()

# Extract records from the response
posts_objs = data.get("data", {}).get("gt_scrape_posts", [])

for post_obj in posts_objs:
    # URL of the webpage you want to scrape
    url = post_obj["url"]

    # Print the URL and ask for user input
    print(f"URL: {url}")
    user_input = input("Do you want to scrape this link? (Yes/No): ").strip().lower()

    # Check if the user wants to scrape the link
    if user_input in ["yes", "y", "YES", "Y", "Yes", "yES", "yeS", "YeS", "yEs", "YEs", "yES", "yEs", "ye", "Ye", "yE", "YE", "ye"]:
        # Headers to mimic a request from a Chrome browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
        }

        # Send a GET request to the webpage
        response = requests.get(url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Target the path with tag names and class names to get content paragraphs
        content_tags = soup.find_all('div', class_='single-content')  # Replace with actual tag and class names

        # Extract content paragraphs
        content_paragraphs = []

        for content_tag in content_tags:
            paragraphs = content_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'])
            for paragraph in paragraphs:
                paragraph_text = paragraph
                if paragraph_text:  # Check if paragraph is not empty after stripping
                    content_paragraphs.append(paragraph_text)

        # Print the content paragraphs
        # for idx, paragraph in enumerate(content_paragraphs, start=1):
        #     print(f"{paragraph}")
        content_paragraphs = " ".join(str(x) for x in content_paragraphs)
        print(content_paragraphs)
        content_paragraphs = f"""\"{content_paragraphs}\"

        The above is the html code with the content in it. I want you to perform the following actions on it and give me the final result without adding any extra text or comment from your side. Just the final result and that's it.
        - Format the html code
        - There are some text tags. I want you to rewrite them and remove the plagirism too. You can add or remove content if needed. Make sure there is enough to read as its a news article and there's no longer content or blog so the reader gets bored.
        - There are some quotes as well. Don't edit them as they're quoted as the words of others except the social media posts.
        - The final result must be in html format that i can pass to wordpress. No extra code as headers or footers or body tag. Just the clean html formatted code.
        - Remove svg code
        - Remove the attributes of all tags except which is not text and which is by the social media website or outer websites e.g twitter, insta, youtube and others
        - Identify twitter posts and replace the post code with the following code and replace with the relevant content or data (Note: Strings to replace are mentioned all caps and underscors, includes TWITTER), might be enclosed in blockquote, you can replace that too
            <center><figure class="wp-block-embed is-type-rich is-provider-twitter wp-block-embed-twitter"><div class="wp-block-embed__wrapper">TWITTER_POST_LINK</div></figure></center>
        - Identify instagram posts and replace the post code with the following code and replace with the relevant content or data (Note: Strings to replace are mentioned all caps and underscors, includes INSTAGRAM)
            <center><figure class="wp-block-embed is-type-rich is-provider-instagram wp-block-embed-instagram"><div class="wp-block-embed__wrapper">INSTAGRAM_POST_LINK</div></figure></center>
        """
        # Copy the text to the clipboard
        pyperclip.copy(content_paragraphs)