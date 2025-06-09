from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography import x509
import secrets
import os
import re
import tempfile
from encrypt.gen_certs import validate_cert

def get_user_private_key(username: str):
    with open(f"./encrypt/Keys/key_{username}.pem", "rb") as f:
        return load_pem_private_key(f.read(), password=None)

def get_user_public_key(cert_path: str):
    with open(cert_path, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())
        return cert.public_key()


def symmetric_encrypt(user, file_to_encrypt, destination_path, algorithm = "AES", cert_path=None):
    print("CERT: ", cert_path)
    if not cert_path or not validate_cert(cert_path, user):
        print("Invalid certificate or user not authorized.")
        return None
    public_key = get_user_public_key(cert_path)
    symmetric_key = secrets.token_bytes(32)
    try:
        with open(file_to_encrypt, "rb") as f:
            data = f.read()

        if algorithm == "AES":
            init_vector = secrets.token_bytes(16)
            padder = sym_padding.PKCS7(128).padder()
            padded_plaintext = padder.update(data) + padder.finalize()
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(init_vector))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            payload =  init_vector + ciphertext
        elif algorithm == "ChaCha20":
            nonce = secrets.token_bytes(16)
            cipher = Cipher(algorithms.ChaCha20(symmetric_key, nonce), mode=None)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data)
            payload = nonce + ciphertext
        elif algorithm == "ARC4":
            cipher = Cipher(algorithms.ARC4(symmetric_key), mode=None)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data)
            payload = ciphertext
        else:
            raise ValueError("Unsupported encryption algorithm")            
        
        
        encrypted_key = public_key.encrypt(
            symmetric_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
                ))
            
        with open(destination_path, "wb") as f:
            f.write(payload)

        os.makedirs(f'./encrypt/Keys/{user}', exist_ok=True)
        with open(f'./encrypt/Keys/{user}/{re.sub(r'[^a-zA-Z0-9_.-]', '_', destination_path)}', "wb") as f:
            f.write(encrypted_key)
        return destination_path
    except Exception as e:
        print(f"An error occurred during encryption: {e}")
        return None


def symmetric_decrypt(user, encrypted_file_path, algorithm = "AES", cert_path=None):
    if not cert_path or not validate_cert(cert_path, user):
        print("Invalid certificate or user not authorized.")
        return None
    try:
        private_key = get_user_private_key(user)
        encrypted_key_path = f"./encrypt/Keys/{user}/{re.sub(r'[^a-zA-Z0-9_.-]', '_', encrypted_file_path)}"
        
        with open(encrypted_key_path, "rb") as f:
            encrypted_key = f.read()

        symmetric_key = private_key.decrypt(
            encrypted_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        if algorithm == "AES":
            with open(encrypted_file_path, "rb") as f:
                init_vector = f.read(16)
                ciphertext = f.read()

            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(init_vector))
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = sym_padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        elif algorithm == "ChaCha20":
            with open(encrypted_file_path, "rb") as f:
                nonce = f.read(16)
                ciphertext = f.read()

            cipher = Cipher(algorithms.ChaCha20(symmetric_key, nonce), mode=None)
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext)
        elif algorithm == "ARC4":
            with open(encrypted_file_path, "rb") as f:
                ciphertext = f.read()

            cipher = Cipher(algorithms.ARC4(symmetric_key), mode=None)
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext)
        else:
            raise ValueError("Unsupported decryption algorithm")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".decrypted", mode="wb") as temp_file:
            temp_file.write(plaintext)
            temp_path = temp_file.name
        return temp_path
        
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None
