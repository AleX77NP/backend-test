from .extensions import bcrypt

def hash_password(password):
    return bcrypt.generate_password_hash(password, 10).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)


