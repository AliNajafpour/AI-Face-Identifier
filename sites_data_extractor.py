from urllib.parse import urljoin
import requests
from boilerpy3 import extractors
from bs4 import BeautifulSoup


def sites_data_scrap_relevant(urls_file: str, filename) -> str:
    '''it extract almost all the relevent data from the site and as much
     as possible wont return irreleant texts only main texts'''
    with open(urls_file, encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('')

    for url in urls:
        try:
            extractor = extractors.CanolaExtractor()
            doc = extractor.get_doc_from_url(url)
            page_contents = doc.content

            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f'{page_contents}\n')
                print(f'saved text from {url}')
        except Exception as e:
            print(f"couldn't access the {url} the error was : {e}")


MIN_TEXT_LENGTH = 200

def fetch_html(url: str) -> str:
    """Fetch page via requests"""
    try:
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=HEADERS, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ''


def parse_html(html: str) -> dict:
    """Extract links, meta, images, and visible text"""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove scripts and styles
    for tag in soup(['script', 'style']):
        tag.decompose()

    # Extract links
    # links = []
    # for a in soup.find_all('a', href=True):
    #     full_url = urljoin(base_url, a['href'])
    #     links.append({'url': full_url, 'text': a.get_text(strip=True)})

    # Extract meta tags
    meta = {}
    for m in soup.find_all('meta'):
        key = m.get('name') or m.get('property')
        if key and m.get('content'):
            meta[key] = m['content']
    if soup.title and soup.title.string:
        meta['title'] = soup.title.string.strip()

    # Extract images
    # images = []
    # for img in soup.find_all('img', src=True):
    #     img_url = urljoin(base_url, img['src'])
    #     images.append({'src': img_url, 'alt': img.get('alt', ''), 'title': img.get('title', '')})

    # Visible text
    text = soup.get_text(separator=' ', strip=True)

    return {
        'links': '',
        'meta': meta,
        'images': 'images',
        'text': text
    }

def sites_data_scrap_all(urls_file: str, filename):
    '''This function extract all texts in a site no matter relevent or
     not to the topic or thay are in important or nat'''
    with open(urls_file, encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('')
    for url in urls:
        html = fetch_html(url)
        if not html:
            continue
        data = parse_html(html)
        # Alert if low text content
        if len(data['text']) < MIN_TEXT_LENGTH:
            print(f"Warning: Low text content for {url}")

        with open(filename, 'a', encoding='utf-8') as f:
            for key, val in data['meta'].items():
                if key == 'description' or key == 'title':
                    f.write(f"{val}\n")
            f.write(data['text'])
