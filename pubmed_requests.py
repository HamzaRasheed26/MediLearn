import requests
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET


class PubMedClient:
    def __init__(self, max_results=10):
        self.base_url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.max_results = max_results

    def fetch_articles(self, query):
        query = f"{quote_plus(query)}[TIAB]"
        """Fetch PubMed article IDs based on the search query."""
        params = {
            'db': 'pubmed',
            'term': quote_plus(query),
            'retmode': 'xml',
            'retmax': self.max_results,
        }
        response = requests.get(self.base_url_search, params=params)
        if response.status_code == 200:
            return self.parse_pubmed_ids(response.text)
        else:
            raise Exception(f"Error fetching articles: {response.status_code}")

    def fetch_article_details(self, article_ids):
        """Fetch detailed information of articles given their IDs."""
        ids = ",".join(article_ids)
        params = {
            'db': 'pubmed',
            'id': ids,
            'retmode': 'xml',
            'rettype': 'abstract',
        }
        response = requests.get(self.base_url_fetch, params=params)
        if response.status_code == 200:
            return self.parse_article_details(response.text)
        else:
            raise Exception(
                f"Error fetching article details: {response.status_code}")

    def parse_pubmed_ids(self, xml_response):
        """Parse PubMed IDs from XML response."""
        root = ET.fromstring(xml_response)
        return [id_elem.text for id_elem in root.findall('.//Id')]

    def parse_article_details(self, xml_response):
        """Parse detailed information (title and abstract) from XML response."""
        root = ET.fromstring(xml_response)
        articles = []
        for article in root.findall('.//PubmedArticle'):
            title = article.find('.//ArticleTitle').text
            abstract = article.find('.//Abstract/AbstractText')
            abstract_text = abstract.text if abstract is not None else 'No abstract available'
            articles.append({'title': title, 'abstract': abstract_text})
        return articles

    def generate_pubmed_urls(self, article_ids):
        """Generate PubMed article URLs from article IDs."""
        base_url = "https://pubmed.ncbi.nlm.nih.gov/"
        return [f"{base_url}{article_id}/" for article_id in article_ids]
