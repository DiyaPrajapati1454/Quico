from database.db import get_connection
from datetime import date

def get_all_delivered_orders():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select order_id,user_id,no_of_quibi,article_no,order_date,delivery_date from orders where status='Delivered' order by order_id
    """)
    orders=cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def get_all_orders():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select order_id,user_id,no_of_quibi,article_no,order_date,delivery_date,status, actual_deliver_date from orders order by order_id
    """)
    orders=cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def get_user_orders(user_id):
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select order_id,no_of_quibi,article_no,order_date,delivery_date,status from orders where user_id=%s order by order_id
    """,(user_id,))
    orders=cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def insert_orders(user_id, qty, aid, ddate):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO orders (user_id, no_of_quibi, article_no,order_date,delivery_date,status)
        VALUES (%s, %s, %s,%s,%s,%s)
    """

    cursor.execute(query, (user_id, qty, aid,date.today(),ddate,"Not Delivered"))
    conn.commit()
    cursor.close()
    conn.close()

def delete_orders(code):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    delete orders
    WHERE order_id=%s
    """
    cursor.execute(query, (code))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_non_deliveredorders():
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("""
    Select order_id,length,width,no_of_quibi,delivery_date from orders,article where orders.status='Not Delivered' and article.code=orders.article_no;
    """)
    orders=cursor.fetchall()
    cursor.close()
    conn.close()
    return orders


from datetime import timedelta

def update_order_status_and_delivery(order_id, status, delivery_date):
    conn =get_connection()
    cursor = conn.cursor()

    query = """
    update orders set actual_deliver_date = %s, status = %s where order_id = %s
    """
    cursor.execute(query,(delivery_date,status,order_id))
    conn.commit()
    cursor.close()
    conn.close()

def load_expected_dates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT order_id, delivery_date FROM orders")

    data = cursor.fetchall()
    conn.close()

    return {order_id: expected_date for order_id, expected_date in data}