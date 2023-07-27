from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import pandas as pd

# Prompt the user for the query
keyword = input("Enter the keyword to search for: ")

# Construct the search URL using the user input
search_url = f"https://ahmia.fi/search/?q={keyword}"

# The URLs of the target websites
urls = [search_url]

# Set up the Tor proxy
proxies = {
    'http': 'socks5h://localhost:9150',
    'https': 'socks5h://localhost:9150'
}

# Load the existing database file if it exists
try:
    database_df = pd.read_excel(f"{keyword}_database.xlsx")
    existing_urls = database_df["URL"].tolist()
except FileNotFoundError:
    database_df = pd.DataFrame(columns=["URL", "Count"])
    existing_urls = []

# Counter variable to limit the display to 20 URLs
counter = 0

# Lists to store the data
url_list = []
count_list = []

# Loop through each website
for url in urls:
    # Send a GET request to the website using the Tor proxy
    response = requests.get(url, proxies=proxies)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the links on the page
    links = soup.find_all("a")

    # Loop through each link and check if it contains the keyword and the .onion domain
    for link in links:
        href = link.get("href")
        if href is not None and keyword in href and ".onion" in href:
            # If the link contains the keyword and the .onion domain, print the URL
            url_parts = urlparse(href)
            if url_parts.scheme == "" or url_parts.netloc == "":
                href = urljoin(url, href)

            # Check if the URL was searched before
            if href not in existing_urls:
                print(href)

                # Send a GET request to the obtained website
                response = requests.get(href, proxies=proxies)
                website_content = response.text

                # Count the occurrences of the keyword in the obtained website
                count = website_content.count(keyword)
                print(f"Count of '{keyword}' in the obtained website: {count}\n")

                # Append the data to the lists
                url_list.append(href)
                count_list.append(count)

                # Increment the counter
                counter += 1

                # Update the existing URLs list
                existing_urls.append(href)

            # Break the loop if the counter reaches 20
            if counter == 20:
                break

    # Break the loop if the counter reaches 20
    if counter == 20:
        break

# Update the database DataFrame
new_data = {'URL': url_list, 'Count': count_list}
new_df = pd.DataFrame(new_data)

# Concatenate the new data with the existing database
updated_df = pd.concat([database_df, new_df])

# Save the updated database to the file
updated_df.to_excel(f"{keyword}_database.xlsx", index=False)

# Prompt the user for the output file name
output_filename = input("Enter the output file name (without extension): ")

# Save the new URLs to the output file
new_urls = new_df["URL"].tolist()
new_urls_df = pd.DataFrame({"URL": new_urls})
new_urls_df.to_excel(f"{output_filename}.xlsx", index=False)

