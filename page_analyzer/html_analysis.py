from bs4 import BeautifulSoup


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
