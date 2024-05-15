import psycopg2
from psycopg2.extras import DictCursor
from functools import wraps


def _with_database_connection(cursor_factory=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with psycopg2.connect(
                    self.database_url,
                    cursor_factory=cursor_factory) as conn:
                with conn.cursor() as cursor:
                    result = func(self, cursor, *args, **kwargs)
            return result
        return wrapper
    return decorator


class Database:
    def __init__(self, database_url):
        self.database_url = database_url

    @_with_database_connection(cursor_factory=DictCursor)
    def get_url_by_id(self, cursor, id):
        cursor.execute(
            "SELECT * FROM urls \
            WHERE id = %s \
            LIMIT 1", (id,))
        url_data = cursor.fetchone()
        return url_data

    @_with_database_connection(cursor_factory=DictCursor)
    def get_all_urls_with_latest_check_time_and_result(self, cursor):
        cursor.execute(
            "SELECT DISTINCT urls.id, \
                urls.name \
            FROM urls \
            ORDER BY urls.id;"
        )
        urls_data = cursor.fetchall()

        cursor.execute(
            "SELECT uc.url_id, \
                uc.status_code, \
                uc.created_at AS latest_check \
            FROM url_checks AS uc \
            JOIN (SELECT url_id, MAX(created_at) AS max_created_at \
                    FROM url_checks \
                    GROUP BY url_id) \
                AS max_uc \
            ON uc.url_id = max_uc.url_id \
                AND uc.created_at = max_uc.max_created_at \
            ORDER BY latest_check DESC;")
        latest_checks = cursor.fetchall()

        urls_with_latest_check = []

        latest_check_map = {check_time['url_id']:
                            (check_time['latest_check'],
                                check_time['status_code'])
                            for check_time in latest_checks}

        for url_data in urls_data:
            url_id = url_data['id']
            name = url_data['name']
            latest_check, status_code = latest_check_map.get(
                url_id, (None, None))
            urls_with_latest_check.append(
                {'id': url_id, 'name': name,
                    'latest_check': latest_check, 'status_code': status_code})

        urls_with_latest_check = list(sorted(
            urls_with_latest_check,
            key=lambda x: (x['latest_check'] is None, x['latest_check']),
            reverse=True))

        return urls_with_latest_check

    @_with_database_connection(cursor_factory=DictCursor)
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
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO url_checks \
                        (url_id, status_code, h1, title, description) \
                        VALUES (%s, %s, %s, %s, %s)",
                        (url_id, status, h1, title, desc))
                    conn.commit()

            except psycopg2.Error as e:
                conn.rollback()
                raise e

    def insert_url_in_urls(self, url):
        with psycopg2.connect(self.database_url) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO urls (name) \
                        VALUES (%s) \
                        RETURNING id", (url,))
                    conn.commit()
                    id = cursor.fetchone()[0]
                    return id

            except psycopg2.Error as e:
                conn.rollback()
                raise e
