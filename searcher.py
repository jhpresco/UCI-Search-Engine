import re

class Searcher:
    def __init__(self, db):
        self.tfidf_collection = db["TfIdf"]
        self.tags_collection = db["Tags"]

    def find(self, query):
        scores = {}
        urls = set({})
        query_words = query.lower().split()

        # Calculate base scores from TF-IDF values
        for term in set(query_words):
            documents = self.tfidf_collection.find({"term": term})
            for doc in documents:
                for url, score in doc['URLs'].items():
                    scores[url] = scores.get(url, 0) + score

        #Adjust scores based on query words presence in important tags
        self._adjust_scores_based_on_tags(scores, query_words)

        # Find top 20 URLs
        #print(scores.items())
        for url, score in scores.items():
            if score > .55:
                #print(url)
                urls.add(url)

        urls = list(urls)
        urls.sort()
        #print(urls)

        return urls[:20]

    def _adjust_scores_based_on_tags(self, scores, query_words):
        # Compile regex for efficiency
        query_regex = '|'.join(re.escape(word) for word in query_words)
        tag_documents = self.tags_collection.find({"tags": {"$in": query_words}})

        for doc in tag_documents:
            url = doc['URL']
            if url not in scores:
                continue  # Skip URLs not already scored

            # Check each tag's words against query words
            for tag, words in doc['tags'].items():
                if re.search(query_regex, ' '.join(words), re.IGNORECASE):
                    # Adjust scores based on tag importance
                    score_adjustment = self._get_tag_score_adjustment(tag)
                    scores[url] += score_adjustment

    def _get_tag_score_adjustment(self, tag):
        # Define score adjustments for different tags
        tag_scores = {
            "title": 2,
            "h1": 1.5,
            "h2": 1,
            "h3": 0.5,
            "b": 0.75
        }
        return tag_scores.get(tag, 0)
