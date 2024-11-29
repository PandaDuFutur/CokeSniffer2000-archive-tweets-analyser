import openpyxl
import requests
from bs4 import BeautifulSoup
import re
import os
import time

def get_archive_links(prefix_url):
    """ Get archive links from Wayback Machine using the CDX Search API """
    # Generate API URL to obtain archives
    query_url = f"https://web.archive.org/cdx/search/cdx?url={prefix_url.replace('https://web.archive.org/web/*/', '')}&output=json"

    print(f"Accès aux archives via : {query_url}")
    
    # Make a GET request to the Wayback Machine API
    response = requests.get(query_url)
    
    if response.status_code != 200:
        print(f"Error accessing Wayback Machine API : {response.status_code}")
        return []

    # Parse le JSON retourné par l'API
    archive_data = response.json()
    
    # Extract archive links (start from index 1 to ignore the header)
    archive_links = [f"https://web.archive.org/web/{entry[1]}/{entry[2]}" for entry in archive_data[1:]]
    
    return archive_links

def scrape_tweet_data(archive_links):
    """ Retrieves and analyzes tweets from archives """
    # Create an Excel file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tweets"
    ws.append(["Capture link", "Tweet"])

    for url in archive_links:
        time.sleep(10)
        print(f"Archive analysis : {url}")
        try:
            # Download the capture page
            tweet_page = requests.get(url)
            if tweet_page.status_code != 200:
                print(f"unable to access {url}. Code : {tweet_page.status_code}")
                continue

            tweet_soup = BeautifulSoup(tweet_page.text, 'html.parser')

            # Extract tweet text
            tweet_text = tweet_soup.find('meta', property='og:description')
            tweet_text = tweet_text['content'] if tweet_text else "Text not found"

            # Add data to Excel
            ws.append([url, tweet_text])

        except Exception as e:
            print(f"Error when processing {url} : {e}")
    
    # Save Excel file
    output_excel = os.path.join(os.getcwd(), "tweets_archive.xlsx")
    wb.save(output_excel)
    print(f"The data was saved in {output_excel}")


def main():
    # Request user prefix
    archive_prefix = input("Please enter archive.org link (par ex. https://web.archive.org/web/*/https://twitter.com/username/status*): ").strip()

    # Check if URL is valid
    if not archive_prefix.startswith("https://web.archive.org/web/*/"):
        print("Wrong link.")
        return

    # Recover archived links
    print(f"Archive retrieval for {archive_prefix}...")
    archive_links = get_archive_links(archive_prefix)

    if not archive_links:
        print("No archive, something wrong?.")
        return

    print(f"{len(archive_links)} archives found. Analysis in progress...")
    
    # Analyze archived pages and extract data
    scrape_tweet_data(archive_links)


# Start script
if __name__ == "__main__":
    main()
