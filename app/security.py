from .extensions import bcrypt
from .models import Korisnik
import string, random
from functools import wraps
from flask import Response, json, session
from .constants import ADMIN, TRAVEL_GUIDE, TOURIST

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

# restrikcije po ulogama

dozvole = {
    ADMIN: 2,
    TRAVEL_GUIDE: 1,
    TOURIST: 0
}

def permisije(tip_naloga):
    def funk(f):
        @wraps(f)
        def dekorisana_funkcija(*args, **kwargs):
            if session.get('korisnik') is None:
                return Response(json.dumps({'poruka': "Niste prijavljeni."}), status=401, mimetype='application/json')
            else:
                tip = vrati_tip_naloga(session.get('korisnik'))
                if dozvole.get(tip) < dozvole.get(tip_naloga):
                    return Response(json.dumps({'poruka': 'Nemate pravo pristupa ovom resursu.'}), status=403, mimetype='application/json')
                else:
                    return f(*args, **kwargs) # ovde bi mogao da se ubaci korisnik da se ne cita stalno iz sesije ? 
        return dekorisana_funkcija
    return funk

