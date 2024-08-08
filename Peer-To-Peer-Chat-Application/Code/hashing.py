import hashlib

class Hashing:

    def encodePassword(self, password):
        result = hashlib.sha512(password.encode())
        return result.hexdigest()
    
