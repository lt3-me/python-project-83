import validators


def validate_url(url):
    if len(url) < 256:
        if validators.url(url) is True:
            return True
        else:
            return False
    else:
        return False
