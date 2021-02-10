from authenticator import HOTP

OTP = HOTP()
# Remove White Space And Useless Characters
def sanitize_secret(secret):
    return secret.replace(' ', '').replace("\n", '').replace("\t", '')

def generate_code_from_time(secret_key, code_length=6, period=30):
    return OTP.generate_code_from_time(secret_key=sanitize_secret(secret_key), code_length=code_length, period=period)

def generate_code_from_counter(secret_key, counter, code_length=6):
    return OTP.generate_code_from_counter(secret_key=sanitize_secret(secret_key), counter=counter, code_length=code_length)

def generate_otp_uri(key, secret_key, alg="totp"):
    return f"otpauth://{alg}/{key}:?secret={secret_key}&issuer={key}"
