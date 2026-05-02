import bcrypt

password = b"sai_12345"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())