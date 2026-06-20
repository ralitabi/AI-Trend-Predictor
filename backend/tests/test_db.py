import sqlite3

from data import db


def test_no_remote_configured_in_tests():
    assert db.is_remote() is False


def test_local_connection_is_sqlite_with_dict_rows():
    conn = db.connect()
    try:
        assert isinstance(conn, sqlite3.Connection)
        row = conn.execute("SELECT 1 AS one, 2 AS two").fetchone()
        # _dict_factory means rows come back as dicts keyed by column name
        assert row == {"one": 1, "two": 2}
    finally:
        conn.close()
