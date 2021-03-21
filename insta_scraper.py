# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 18:44:46 2021
@author: Kossi Eloi Fabius Defly
"""

from bs4 import BeautifulSoup
import json
import cloudscraper
import pymongo

post_image = ""
post_text = ""
post_comments_url = ""
post_comments = []
db_client = pymongo.MongoClient("mongodb://localhost:27017/")
mycol = db_client["scraping_db"]["insta"]

""" la fonction get_posts prends en paramètres url et le type d'élément à retourné(soit le post soit les commentaires) """
def get_posts(url, post_type):
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    
    scripts = soup.findAll('script', {'type': 'text/javascript'})[3]
    clean_data = str(scripts).replace(';</script>', '').replace('<script type="text/javascript">window._sharedData = ', '')
    
    json_data = json.loads(clean_data)
    if post_type == "posts":
        return json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    else:
        return json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']

        
"""la fonction extract_data prends en paramètre les posts reourner, extrait les données(text, image) ensuite il fait une 
requête pour récupérer les commentaire et les ajoute dans une liste pour finir elle s'occupe de l'insertion des données 
dans la base de données"""
def extract_data(post):
    post_image = post['node']['display_url']
    post_text = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
    post_comments_url = 'https://www.instagram.com/p/' + post['node']['shortcode']
    
    comments = get_posts(post_comments_url, "comments")
    for comment in comments:
        post_comments.append(comment['node']['text'])
        
    print(post_comments_url, post_comments)
    mydict = { "image": post_image, "text": post_text, "comments": post_comments }
    insert = mycol.insert_one(mydict)
        
    
"""la fonction main est le point de lancement du processus"""      
def main():
   posts = get_posts("https://www.instagram.com/explore/tags/jacqueschiracdeces/", "posts")
   
   for post in posts:
       extract_data(post)
       
if __name__ == "__main__":
    main()