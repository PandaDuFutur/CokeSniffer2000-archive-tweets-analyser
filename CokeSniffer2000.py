import openpyxl
import requests
from bs4 import BeautifulSoup
import re
import os
import time

def get_archive_links(prefix_url):
    """ Récupère les liens d'archives depuis Wayback Machine en utilisant l'API de recherche CDX """
    # Générer l'URL d'API pour obtenir les archives
    query_url = f"https://web.archive.org/cdx/search/cdx?url={prefix_url.replace('https://web.archive.org/web/*/', '')}&output=json"

    print(f"Accès aux archives via : {query_url}")
    
    # Faire une requête GET à l'API de Wayback Machine
    response = requests.get(query_url)
    
    if response.status_code != 200:
        print(f"Erreur en accédant à l'API de Wayback Machine : {response.status_code}")
        return []

    # Parse le JSON retourné par l'API
    archive_data = response.json()
    
    # Extraire les liens d'archive (on commence à partir de l'index 1 pour ignorer l'en-tête)
    archive_links = [f"https://web.archive.org/web/{entry[1]}/{entry[2]}" for entry in archive_data[1:]]
    
    return archive_links

def scrape_tweet_data(archive_links):
    """ Récupère et analyse les tweets depuis les archives """
    # Créer un fichier Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tweets"
    ws.append(["Lien de capture", "Tweet"])

    for url in archive_links:
        time.sleep(10)
        print(f"Analyse de l'archive : {url}")
        try:
            # Télécharger la page de la capture
            tweet_page = requests.get(url)
            if tweet_page.status_code != 200:
                print(f"Impossible d'accéder à {url}. Code : {tweet_page.status_code}")
                continue

            tweet_soup = BeautifulSoup(tweet_page.text, 'html.parser')

            # Extraire le texte du tweet
            tweet_text = tweet_soup.find('meta', property='og:description')
            tweet_text = tweet_text['content'] if tweet_text else "Texte introuvable"

            # Ajouter les données dans l'Excel
            ws.append([url, tweet_text])

        except Exception as e:
            print(f"Erreur lors du traitement de {url} : {e}")
    
    # Sauvegarder le fichier Excel
    output_excel = os.path.join(os.getcwd(), "tweets_archive.xlsx")
    wb.save(output_excel)
    print(f"Les données ont été sauvegardées dans {output_excel}")


def main():
    # Demander le préfixe de l'utilisateur
    archive_prefix = input("Entrez le préfixe d'archive.org (par ex. https://web.archive.org/web/*/https://twitter.com/username/status*): ").strip()

    # Vérifier si l'URL est valide
    if not archive_prefix.startswith("https://web.archive.org/web/*/"):
        print("Lien invalide. Assurez-vous qu'il correspond au format attendu.")
        return

    # Récupérer les liens archivés
    print(f"Récupération des archives pour {archive_prefix}...")
    archive_links = get_archive_links(archive_prefix)

    if not archive_links:
        print("Aucune archive trouvée.")
        return

    print(f"{len(archive_links)} archives trouvées. Analyse en cours...")
    
    # Analyser les pages archivées et extraire les données
    scrape_tweet_data(archive_links)


# Exécution du script
if __name__ == "__main__":
    main()
