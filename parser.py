from html.parser import HTMLParser
import re

# Jack Zeng: lxml and beautifulsoup have various problem on solving mixtures of html,xml and other files

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.content_data = []
        self.important_tags_data = {'h1': set(), 'h2': set(), 'h3': set(), 'b': set(), 'title': set()}

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False

    def handle_data(self, data):
        if self.in_body and self.lasttag != "script" or self.lasttag == "title":
            self.content_data.append(data)
        if self.lasttag in self.important_tags_data:
            words = set(filter(None, re.split("[^a-z0-9]+", data.lower())))
            self.important_tags_data[self.lasttag].update(words)

    def get_content(self):
        return ' '.join(self.content_data)

    def get_important_words(self):
        return {tag: list(words) for tag, words in self.important_tags_data.items()}
