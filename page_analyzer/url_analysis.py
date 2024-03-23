import requests
from bs4 import BeautifulSoup


def check_url(url):
    r = requests.get(url=url)
    try:
        r.raise_for_status()
        status_code = r.status_code
        html_content = r.text
        h1, title, desc = extract_elements_from_html(html_content)
        return {'status_code': status_code, 'h1': h1,
                'title': title, 'description': desc}
    except requests.exceptions.HTTPError:
        return None


def extract_elements_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h1 = soup.find('h1')
    h1 = h1.text.strip() if h1 else None
    title = soup.title
    title = title.text.strip() if title else None

    description = None
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        description = meta_tag['content'].strip()

    return h1, title, description
