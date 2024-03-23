import validators


def validate_url(url):
    errors = {}
    if len(url) > 255:
        errors['length_error'] = 'URL превышает 255 символов'
    if not validators.url(url):
        errors['validate_error'] = 'Некорректный URL'
    return errors
