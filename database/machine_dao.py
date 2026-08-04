from database.db import get_connection
from datetime import date

def get_all_machines():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select m_id,m_name,max_width,speed,m_type,status from machine
    """)
    machines=cursor.fetchall()
    cursor.close()
    conn.close()
    return machines

def get_all_cutting_machines():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select m_id,m_name,max_width,speed from machine where status='active' and m_type='Cutting'
    """)
    cutting=cursor.fetchall()
    cursor.close()
    conn.close()
    return cutting

def get_all_folding_machines():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select m_id,m_name,max_width,speed from machine where status='active' and m_type='Folding'
    """)
    folding=cursor.fetchall()
    cursor.close()
    conn.close()
    return folding

def get_all_packing_machines():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select m_id,m_name,max_width,speed from machine where status='active' and m_type='Packing'
    """)
    packing=cursor.fetchall()
    cursor.close()
    conn.close()
    return packing

def insert_machine(m_name, width, speed, m_type, status):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO machine (m_name, max_width, speed,m_type,status,created_at,updated_at)
        VALUES (%s, %s, %s,%s,%s,%s,%s)
    """

    cursor.execute(query, (m_name, width, speed,m_type,status,date.today(),date.today()))
    conn.commit()
    cursor.close()
    conn.close()

def insert_machine_setup_time(m_id,min_length,max_length,duration):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO machine_setup_time (machine_id, min_length_diff,max_length_diff,duration)
        VALUES (%s, %s, %s,%s)
    """

    cursor.execute(query, (m_id,min_length,max_length,duration))
    conn.commit()
    cursor.close()
    conn.close()

def update_machine(code, m_name, width, speed, m_type, status):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    UPDATE machine
    SET m_name=%s, max_width=%s, speed=%s, m_type=%s, status=%s, updated_at=%s
    WHERE m_id=%s
    """
    cursor.execute(query, (m_name, width, speed,m_type, status,date.today(),code))
    conn.commit()
    cursor.close()
    conn.close()

def delete_machine(code):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    UPDATE machine
    SET status=%s, updated_at=%s
    WHERE m_id=%s
    """
    cursor.execute(query, ("Inactive",date.today(),code))
    conn.commit()
    cursor.close()
    conn.close()

def get_setup_times_by_machine(machine_id):
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select min_length_diff, max_length_diff, duration from machine_setup_time where machine_id=machine_id
    """)
    packing=cursor.fetchall()
    cursor.close()
    conn.close()
    return packing