from database.db import get_connection
from datetime import date

def get_all_articles():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select code,length,width,status from article order by code
    """)
    articles=cursor.fetchall()
    cursor.close()
    conn.close()
    return articles

def insert_article(code, length, width, status):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO article (code, length, width,status,created_at,updated_at)
        VALUES (%s, %s, %s,%s,%s,%s)
    """

    cursor.execute(query, (code, length, width,status,date.today(),date.today()))
    conn.commit()
    cursor.close()
    conn.close()

def update_article(old_code, new_code, length, width, status):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    UPDATE article
    SET code=%s, length=%s, width=%s, status=%s, updated_at=%s
    WHERE code=%s
    """
    cursor.execute(query, (new_code, length, width,status,date.today(),old_code))
    conn.commit()
    cursor.close()
    conn.close()

def delete_article(code):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    UPDATE article
    SET status=%s, updated_at=%s
    WHERE code=%s
    """
    cursor.execute(query, ("Inactive",date.today(),code))
    conn.commit()
    cursor.close()
    conn.close()
