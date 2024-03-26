import psycopg2
from functools import wraps


class URLsDatabaseController:
    def __init__(self, database_url):
        self.database_url = database_url

    def _with_database_connection():
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                with psycopg2.connect(self.database_url) as conn:
                    with conn.cursor() as cursor:
                        result = func(self, cursor, *args, **kwargs)
                return result
            return wrapper
        return decorator

    @_with_database_connection()
    def get_url_by_id(self, cursor, id):
        cursor.execute(
            "SELECT * FROM urls \
            WHERE id = %s \
            LIMIT 1", (id,))
        url_data = cursor.fetchone()
        return url_data

    @_with_database_connection()
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
            ORDER BY latest_check DESC;"
            )
        latest_check_times = cursor.fetchall()

        urls_with_latest_check = []

        for url_data in urls_data:
            url_id = url_data[0]
            name = url_data[1]
            status_code = url_data[2]
            latest_check = None
            for check_time in latest_check_times:
                if check_time[0] == url_id:
                    latest_check = check_time[1]
                    break
            urls_with_latest_check.append(
                (url_id, name, latest_check, status_code))

        urls_with_latest_check = list(sorted(
            urls_with_latest_check,
            key=lambda x: (x[2] is None, x[2]),
            reverse=True))

        return urls_with_latest_check

    @_with_database_connection()
    def get_url_checks_by_url_id(self, cursor, url_id):
        cursor.execute(
            "SELECT * FROM url_checks \
            WHERE url_id = %s \
            ORDER BY created_at DESC", (url_id,))
        url_checks = cursor.fetchall()
        return url_checks

    def try_insert_page_check(self, url_id, status, h1, title, desc):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "INSERT INTO url_checks \
                        (url_id, status_code, h1, title, description) \
                        VALUES (%s, %s, %s, %s, %s)",
                        (url_id, status, h1, title, desc))
                    conn.commit()
                    return 'check_insert_success'
                except psycopg2.Error as e:
                    print(e.pgerror)
                    print(e.diag.message_primary)
                    return 'insert_error'

    def try_insert_url_in_urls(self, url):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(
                        "SELECT * FROM urls \
                        WHERE name = %s \
                        LIMIT 1", (url,))
                    entry = cursor.fetchone()

                    if not entry:
                        cursor.execute(
                            "INSERT INTO urls (name) \
                            VALUES (%s) \
                            RETURNING id", (url,))
                        conn.commit()
                        id = cursor.fetchone()[0]
                        status = 'success'
                    else:
                        id = entry[0]
                        status = 'exists'

                except psycopg2.Error:
                    print(psycopg2.Error)
                    conn.rollback()
                    id = None
                    status = 'insert_error'

                finally:
                    return (id, status)
