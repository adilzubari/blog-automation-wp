import requests
from bs4 import BeautifulSoup

# Hasura server URL
hasura_url = "https://nexus-logix.hasura.app/v1/graphql"

# Admin secret for authentication
admin_secret = "g7nPwES1QWyhT1HLAJnWvvGGWx6ZjzhmT1gYKP2h6eVjf0vaWvuVKHnMi9UZTc3U"

# GraphQL query to fetch records
graphql_query = """
{
  gt_scrape_weblinks {
    id
    title
    link
    target_class
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
url_objects = data.get("data", {}).get("gt_scrape_weblinks", [])
print("URL objects:", url_objects)

# url_objects  = [
#     {
#         "url": "https://arynews.tv/category/international-2/",
#         "target_class": "entry-title",
#     }
# ]

# Headers to mimic a Chrome browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

for url_obj in url_objects:
    url = url_obj["link"]
    target_class = url_obj["target_class"]
    id = url_obj["id"]

    print("URL:", url)
    print("Target class:", target_class)

    # Send an HTTP GET request to the URL
    response = requests.get(url, headers=headers)
    print(response.status_code)  # Print the status code

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all elements with the target class
    elements_with_class = soup.find_all(class_=target_class)

    # Loop through each element and extract information
    for element in elements_with_class:

        link_element = element.find("a")
        if link_element:
            # Extract the link
            link = link_element["href"]
            if not link.startswith("http"):
                link = "https://www.geo.tv" + link
            

            # Prepare GraphQL mutation to insert or update a record
            mutation = """
            mutation InsertOrUpdateLink($link: String!, $id: String!) {
            insert_gt_scrape_posts_one(
                object: {url: $link, gt_scrape_weblink_id: $id},
                on_conflict: {constraint: gt_scrape_posts_pkey, update_columns: [url]}
            ) {
                id
            }
            }
            """

            # Prepare variables for the mutation
            mutation_variables = { "link": link, "id": id }

            # Create the mutation payload
            mutation_payload = {
                "query": mutation,
                "variables": mutation_variables
            }

            # Send the mutation request to the Hasura server
            mutation_response = requests.post(hasura_url, json=mutation_payload, headers=graphql_headers)

        else:
            link = "Link not found"

        # Print the extracted information
        print("Link:", link)
        print("-" * 50)  # Separator between posts
