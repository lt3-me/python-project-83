import psycopg2
from functools import wraps
from .url_analysis import check_url


class URLsDatabaseController:
    def __init__(self, database_url):
        self.database_url = database_url

    def _with_database_connection(*, with_conn_as_arg=False):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                conn = psycopg2.connect(self.database_url)
                cursor = conn.cursor()
                if with_conn_as_arg:
                    result = func(self, conn, cursor, *args, **kwargs)
                else:
                    result = func(self, cursor, *args, **kwargs)
                cursor.close()
                conn.close()
                return result
            return wrapper
        return decorator

    @_with_database_connection()
    def get_url_data_for_id(self, cursor, id):
        cursor.execute(
            "SELECT * FROM urls \
            WHERE id = %s \
            LIMIT 1", (id,))
        url_data = cursor.fetchone()
        return url_data

    @_with_database_connection()
    def get_all_urls(self, cursor):
        cursor.execute("SELECT * FROM urls")
        urls_data = cursor.fetchall()
        return urls_data

    @_with_database_connection()
    def get_all_url_checks_for_url_id(self, cursor, url_id):
        cursor.execute(
            "SELECT * FROM url_checks \
            WHERE url_id = %s \
            ORDER BY created_at DESC", (url_id,))
        url_checks = cursor.fetchall()
        return url_checks

    @_with_database_connection(with_conn_as_arg=True)
    def try_check_url_by_id(self, conn, cursor, id):
        url_id, url, _ = self.get_url_data_for_id(id)
        page_data = check_url(url)
        if page_data:
            try:
                print(page_data)
                status, h1, title, desc = page_data.values()
                print(status)
                cursor.execute(
                    "INSERT INTO url_checks \
                    (url_id, status_code, h1, title, description) \
                    VALUES (%s, %s, %s, %s, %s)",
                    (url_id, status, h1, title, desc))
                conn.commit()
                return 'success'
            except psycopg2.Error as e:
                print(e.pgerror)
                print(e.diag.message_primary)
                return 'insert_error'
        else:
            return 'request_error'

    @_with_database_connection(with_conn_as_arg=True)
    def try_insert_url_in_urls(self, conn, cursor, url):
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
            status = 'error'

        finally:
            return (id, status)
