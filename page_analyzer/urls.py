import validators
from urllib.parse import urlparse


def validate_url(url):
    errors = []
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
    if not validators.url(url):
        errors.append('Некорректный URL')
    return errors


def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme + '://' + parsed_url.netloc
