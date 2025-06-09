from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
import datetime
import os

cert_directory = r".\encrypt"
keys_dir = cert_directory + r"\Keys"
user_ca_dir = cert_directory + r"\UserCerts"

def init():
    if not os.path.exists(keys_dir):
        os.mkdir(keys_dir)

    if not os.path.exists(user_ca_dir):
        os.mkdir(user_ca_dir)

    ca_key = rsa.generate_private_key(65537, 4096)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "SKVimes"),
    ])

    ca_cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
        .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now())
        .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical= True)
        .sign(ca_key, hashes.SHA256()))

    with open(cert_directory + r"\ca_key.pem", "wb") as f:
        f.write(ca_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))
    with open(cert_directory + r"\ca.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

def user_ca(username, shelf_life=3600):

    with open(cert_directory + r"\ca_key.pem", "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(cert_directory + r"\ca.pem", "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())

    user_ca_key = rsa.generate_private_key(65537, 2048)
    user_csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, username)]))
        .sign(user_ca_key, hashes.SHA256())
    )
    with open(keys_dir + "\\key_" + username + ".pem", "wb") as f:
        f.write(user_ca_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))
    user_cert = (
        x509.CertificateBuilder()
        .subject_name(user_csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(user_csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now())
        .not_valid_after(datetime.datetime.now() + datetime.timedelta(seconds= shelf_life))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    with open(user_ca_dir+ "\\"+ username + ".pem", "wb") as f:
         f.write(user_cert.public_bytes(serialization.Encoding.PEM))

def validate_cert(cert_path, username):
    print(f"Validating certificate at {cert_path} for user {username}")
    try:
        with open(cert_path, "rb") as f:
            user_cert = x509.load_pem_x509_certificate(f.read())
        with open(cert_directory + r"\ca.pem", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        now = datetime.datetime.now()
        print(f"HEREERRRE {now} compared to {user_cert.not_valid_before}, {user_cert.not_valid_after}")
        if now < user_cert.not_valid_before or now > user_cert.not_valid_after:
            print("Certificate is not valid at this time.")
            return False
        ca_cert.public_key().verify(
            user_cert.signature,
            user_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        subject = user_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        if subject != username:
            return False

        return True
    except Exception as e:
        print(f"Certificate validation failed: {e}")
        return False

if __name__ == "__main__":
    init()