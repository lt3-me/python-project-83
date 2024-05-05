import validators


def validate_url(url):
    errors = []
    if len(url) > 255:
        errors.append('URL превышает 255 символов')
    if not validators.url(url):
        errors.append('Некорректный URL')
    return errors
