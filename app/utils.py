from passlib.context import CryptContext
'''
    This module contains utility functions for password hashing and verification.
'''

# The CryptContext is used to manage password hashing schemes. In this case, it is configured to use the bcrypt hashing algorithm, which is a secure and widely used method for hashing passwords.  
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return crypt.hash(password)


# The verify_password function checks if a given plain password matches the hashed password stored in the database. It uses the CryptContext to perform the verification, returning True if the passwords match and False otherwise.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypt.verify(plain_password, hashed_password)