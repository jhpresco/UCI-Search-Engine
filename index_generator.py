import json
import os
import math
import re
from urllib.parse import urlparse, parse_qs
import urllib.request
from parser import Parser
from tqdm import tqdm
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np


nltk.download('wordnet')
nltk.download('stopwords')

# Reference: https://www.geeksforgeeks.org/removing-stop-words-nltk-python/
stop_words = set(stopwords.words("english"))

# Reference: https://www.geeksforgeeks.org/python-lemmatization-with-nltk/
lemmatizer = WordNetLemmatizer()


def create_db(client, tf_idf, important_tags):
    db = client.SearchEngine_Normalized
    for term, urls in tf_idf.items():
        db.TfIdf.insert_one({'term': term, 'URLs': urls})
    for url, tags in important_tags.items():
        db.Tags.insert_one({'URL': url, "tags": tags})


class WebPageIndexer:
    PATH = "WEBPAGES_RAW/bookkeeping.json"

    def __init__(self):
        with open(self.PATH, 'r', encoding='utf-8') as f:
            self.file_url_map = json.load(f)
        self.url_file_map = {url: file for file, url in self.file_url_map.items()}

    def get_file_path(self, url):
        directory, filename = self.url_file_map[url].split('/')
        return os.path.join( "WEBPAGES_RAW", directory, filename)

    def process_urls(self, client):
        tf = {}
        df = {}
        tf_idf = {}
        important_tags = {}
        valid_doc_count = 0
        urls = list(self.url_file_map.keys())

        for url in tqdm(urls, desc="Processing URLs", colour="WHITE"):
            if url not in tf and self.is_trap(url):
                valid_doc_count += 1
                with open(self.get_file_path(url), 'r', encoding='utf-8') as file:
                    parser = Parser()
                    parser.feed(file.read())

                text = parser.get_content()
                # Split text into words, filter out stop words, apply lemmatization, and convert to lowercase
                words = [lemmatizer.lemmatize(word).lower() for word in re.split("[^a-z0-9]+", text.lower())
                        if word and word not in stop_words]
                tf[url] = {}
                word_set = set()

                for word in words:
                    tf[url][word] = tf[url].get(word, 0) + 1
                    if word not in word_set:
                        df[word] = df.get(word, 0) + 1
                        word_set.add(word)

                important_tags[url] = parser.get_important_words()

        for doc, terms in tf.items():
            for term in terms:
                tf_idf.setdefault(term, {})[doc] = (1 + math.log(terms[term], 10)) * math.log(
                    valid_doc_count / df[term], 10)
                
        for term, docs in tf_idf.items():
            max_tfidf = max(docs.values())
            for doc in docs:
                tf_idf[term][doc] /= max_tfidf

        create_db(client, tf_idf, important_tags)

    # def is_trap(self, url):
    #     parsed = urlparse(url)
    #     if re.search(r"(?:/.+?){10,}", parsed.path):
    #         return False

    #     if parsed.query:
    #         past_urls = list(self.url_file_map.keys())
    #         queries = set(parse_qs(parsed.query))
    #         similar_count = sum(1 for past_url in past_urls if set(parse_qs(urlparse(past_url).query)) == queries)

    #         if similar_count >= 10:
    #             return False
    #     return True
        
    def is_trap(self, url):
        try:
            parsed = urlparse(url)
        except:
            return False
        if len(url) >= 255: return False
        return True
