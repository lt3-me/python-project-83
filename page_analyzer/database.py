import psycopg2
from psycopg2.extras import DictCursor
from functools import wraps


class URLsDatabaseController:
    def __init__(self, database_url):
        self.database_url = database_url

    def _with_database_connection(dict_cursor=False):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                cf = DictCursor if dict_cursor else None
                with psycopg2.connect(
                        self.database_url, cursor_factory=cf) as conn:
                    with conn.cursor() as cursor:
                        result = func(self, cursor, *args, **kwargs)
                return result
            return wrapper
        return decorator

    @_with_database_connection(dict_cursor=True)
    def get_url_by_id(self, cursor, id):
        cursor.execute(
            "SELECT * FROM urls \
            WHERE id = %s \
            LIMIT 1", (id,))
        url_data = cursor.fetchone()
        return url_data

    @_with_database_connection(dict_cursor=True)
    def get_all_urls_with_latest_check_time_and_result(self, cursor):
        cursor.execute(
            "SELECT DISTINCT urls.id, \
                    urls.name, \
                    uc.status_code \
            FROM urls \
            LEFT JOIN url_checks AS uc ON urls.id = uc.url_id \
            ORDER BY urls.id;"
        )
        urls_data = cursor.fetchall()

        cursor.execute(
            "SELECT \
                uc.url_id, \
                MAX(uc.created_at) AS latest_check \
            FROM url_checks AS uc \
            GROUP BY uc.url_id \
            ORDER BY latest_check DESC;")
        latest_check_times = cursor.fetchall()

        urls_with_latest_check = []

        latest_check_map = {check_time['url_id']: check_time['latest_check']
                            for check_time in latest_check_times}

        for url_data in urls_data:
            url_id = url_data['id']
            name = url_data['name']
            status_code = url_data['status_code']
            latest_check = latest_check_map.get(url_id, None)
            urls_with_latest_check.append(
                {'id': url_id, 'name': name,
                    'latest_check': latest_check, 'status_code': status_code})

        urls_with_latest_check = list(sorted(
            urls_with_latest_check,
            key=lambda x: (x['latest_check'] is None, x['latest_check']),
            reverse=True))

        return urls_with_latest_check

    @_with_database_connection(dict_cursor=True)
    def get_url_checks_by_url_id(self, cursor, url_id):
        cursor.execute(
            "SELECT * FROM url_checks \
            WHERE url_id = %s \
            ORDER BY created_at DESC", (url_id,))
        url_checks = cursor.fetchall()
        return url_checks

    @_with_database_connection()
    def get_url_id_by_url(self, cursor, url):
        cursor.execute(
            "SELECT * FROM urls \
            WHERE name = %s \
            LIMIT 1", (url,))
        entry = cursor.fetchone()
        if entry:
            return entry[0]

        return None

    def insert_page_check(self, check_data):
        url_id, status, h1, title, desc = check_data
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO url_checks \
                        (url_id, status_code, h1, title, description) \
                        VALUES (%s, %s, %s, %s, %s)",
                        (url_id, status, h1, title, desc))
                    conn.commit()

                except psycopg2.Error:
                    conn.rollback()
                    raise ValueError

    def insert_url_in_urls(self, url):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO urls (name) \
                        VALUES (%s) \
                        RETURNING id", (url,))
                    conn.commit()
                    id = cursor.fetchone()[0]
                    return id

                except psycopg2.Error:
                    conn.rollback()
                    raise ValueError
