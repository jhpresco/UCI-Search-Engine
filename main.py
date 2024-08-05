import sys

from index_generator import WebPageIndexer
from pymongo import MongoClient
from searcher import Searcher

def initialize_index(client):
    if 'SearchEngine_Normalized' not in client.list_database_names():
        print("Initializing the index. Please wait...")
        indexer = WebPageIndexer()
        indexer.process_urls(client)
        print("Indexing complete.")
    else:
        print("There's an available database now")

def search_loop(searcher):
    while True:
        key_word = input("Please input key word (type exit to end search): ").strip()
        while not key_word:
            key_word = input("Enter a valid key word: ").strip()

        if key_word == "exit":
            sys.exit()

        ranked_results = searcher.find(key_word)

        if len(ranked_results) == 0:
            print("Sorry, no relevant documents were found")

        for result in ranked_results:
            print(result)


if __name__ == "__main__":
    client = MongoClient(port=27017)
    initialize_index(client)
    db = client["SearchEngine_Normalized"]
    searcher = Searcher(db)
    search_loop(searcher)
