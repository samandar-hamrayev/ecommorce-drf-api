from datetime import timedelta
from random import  randint
from django.utils.timezone import now


def generate_verification_code():
    return f"{randint(100_000, 999_999)}"

def get_expiry_time():
    return now() + timedelta(minutes=10)