import pytest
import asyncio
import aiomysql
import os


@pytest.mark.asyncio
async def test_mariadb_connection():
    """Test connection to MariaDB database"""
    try:
        connection = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="memo_user",
            password="phoenix",
            db="memo_app"
        )

        assert connection is not None

        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            assert result == (1,)

        connection.close()

    except Exception as e:
        pytest.fail(f"Failed to connect to MariaDB: {e}")


@pytest.mark.asyncio
async def test_mariadb_database_exists():
    """Test that the memo_app database exists"""
    try:
        connection = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="memo_user",
            password="phoenix",
            db="memo_app"
        )

        async with connection.cursor() as cursor:
            await cursor.execute("SHOW DATABASES LIKE 'memo_app'")
            result = await cursor.fetchone()
            assert result is not None
            assert result[0] == "memo_app"

        connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify database exists: {e}")


@pytest.mark.asyncio
async def test_mariadb_memos_table_exists():
    """Test that the memos table exists"""
    try:
        connection = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="memo_user",
            password="phoenix",
            db="memo_app"
        )

        async with connection.cursor() as cursor:
            await cursor.execute("SHOW TABLES LIKE 'memos'")
            result = await cursor.fetchone()
            assert result is not None
            assert result[0] == "memos"

        connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify memos table exists: {e}")


@pytest.mark.asyncio
async def test_mariadb_memos_table_structure():
    """Test the structure of the memos table"""
    try:
        connection = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="memo_user",
            password="phoenix",
            db="memo_app"
        )

        async with connection.cursor() as cursor:
            await cursor.execute("DESCRIBE memos")
            columns = await cursor.fetchall()

            column_names = [col[0] for col in columns]

            expected_columns = [
                'id', 'title', 'content', 'tags', 'priority',
                'category', 'is_archived', 'is_favorite', 'author',
                'created_at', 'updated_at'
            ]

            for expected_col in expected_columns:
                assert expected_col in column_names, f"Column {expected_col} not found in memos table"

        connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify memos table structure: {e}")


@pytest.mark.asyncio
async def test_mariadb_insert_and_retrieve():
    """Test inserting and retrieving data from memos table"""
    try:
        connection = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="memo_user",
            password="phoenix",
            db="memo_app"
        )

        async with connection.cursor() as cursor:
            # Insert test data
            await cursor.execute(
                """
                INSERT INTO memos (title, content, priority)
                VALUES (%s, %s, %s)
                """,
                ("Integration Test Memo", "This is a test memo for integration testing", 2)
            )
            await connection.commit()

            # Retrieve the inserted data
            await cursor.execute(
                """
                SELECT title, content, priority
                FROM memos
                WHERE title = %s
                """,
                ("Integration Test Memo",)
            )
            result = await cursor.fetchone()

            assert result is not None
            assert result[0] == "Integration Test Memo"
            assert result[1] == "This is a test memo for integration testing"
            assert result[2] == 2

            # Clean up - delete the test data
            await cursor.execute(
                "DELETE FROM memos WHERE title = %s",
                ("Integration Test Memo",)
            )
            await connection.commit()

        connection.close()

    except Exception as e:
        pytest.fail(f"Failed to insert and retrieve data: {e}")
