from .extensions import bcrypt
from .models import Korisnik
import string, random

# hesiranje lozinke i provera 
def hash_password(password):
    return bcrypt.generate_password_hash(password, 10).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)

# provera uloge
def vrati_tip_naloga(korisnik):
    tip = Korisnik.query.filter_by(korisnicko_ime=korisnik).with_entities(Korisnik.tip_naloga).first()
    return tip[0]

# generisi kod za resetovanje lozinke
def generisi_reset_token():
    return ''.join(random.choice(string.ascii_lowercase) for x in range(24))

