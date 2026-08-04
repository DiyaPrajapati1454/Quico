import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password, hashed):
    """
    Returns True if password matches the stored hashed password
    """
    return bcrypt.checkpw(password.encode(), hashed.encode())
