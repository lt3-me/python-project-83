import validators


def validate_url(url):
    if len(url) < 256:
        if validators.url(url) is True:
            return True
        else:
            print('Validation Failure')
            return False
    else:
        print(f'URL {url} is too long')
        return False
