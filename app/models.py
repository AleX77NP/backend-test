from .extensions import db

# Klasa Aranzman
class Aranzman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opis = db.Column(db.Text, nullable=False)
    destinacija = db.Column(db.String(50), nullable=False)
    broj_mesta = db.Column(db.Integer, nullable=False)
    cena = db.Column(db.Float, nullable=False)
    pocetak = db.Column(db.DateTime, nullable=False)
    kraj = db.Column(db.DateTime, nullable=False)


# klasa Korisnik
class Korisnik(db.Model):
    ime = db.Column(db.String(20), nullable=False)
    prezime = db.Column(db.String(30), nullable=False)
    email =  db.Column(db.String(50), primary_key=True, nullable=False)
    korisnicko_ime = db.Column(db.String(50), unique=True, nullable=False)
    lozinka =  db.Column(db.String(20), nullable=False)
    tip_naloga = db.Column(db.String(15), nullable=False, default='TOURIST')

# Klasa rezervacija
class Rezervacija(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aranzman = db.Column(db.Integer, db.ForeignKey('aranzman.id'), nullable=False)
    korisnik = db.Column(db.String(50), db.ForeignKey('korisnik.email'), nullable=False)
    broj_mesta = db.Column(db.Integer, nullable=False)
    ukupna_cena = db.Column(db.Float, nullable=False)


# Klasa Zahtev za nadogradnju profila
class Zahtev(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    podnosilac = db.Column(db.String(15), db.ForeignKey('korisnik.email'), nullable=False)
    zeljeni_nalog = db.Column(db.String(15), nullable=False)


    
