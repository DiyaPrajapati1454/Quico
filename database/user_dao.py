from database.db import get_connection
from utils.security import hash_password
from utils.security import check_password
from datetime import date

def insert_user(username, email, password_hash,role):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO user (uname, email, password,role,created_at,updated_at)
        VALUES (%s, %s, %s,%s,%s,%s)
    """

    cursor.execute(query, (username, email, password_hash,role,date.today(),date.today()))
    conn.commit()

    cursor.close()
    conn.close()

def authenticate_user(email, password):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT uid, uname, email, password, role
            FROM user
            WHERE email = %s 
        """

        cursor.execute(query, (email.strip().lower(),))
        user = cursor.fetchone()

        if not user:
            return None
        if not check_password(password,user["password"]):
            return None
        user.pop("password")
        return user
    except Exception as e:
        print("Authentication Error:", e)
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
def get_user_by_id(user_id):
    conn=None
    conn=get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT uid, uname, email FROM user WHERE uid = %s", (user_id,))
    return cursor.fetchone()

def get_user_by_email(email):
    conn=None
    conn=get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    return cursor.fetchone()


def update_user_profile(user_id, username, email):
    conn=None
    conn=get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user SET uname=%s, email=%s, updated_at=%s WHERE uid=%s
    """, (username, email, date.today(), user_id))
    conn.commit()

def update_password(email, password):
    conn=None
    conn=get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user SET password = %s, updated_at=%s WHERE email = %s",
        (password, date.today(),email)
    )
    conn.commit()


