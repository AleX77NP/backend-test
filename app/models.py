from .extensions import db
from .constants import NA_CEKANJU

# klasa Korisnik
class Korisnik(db.Model):
    ime = db.Column(db.String(20), nullable=False)
    prezime = db.Column(db.String(30), nullable=False)
    email =  db.Column(db.String(50), unique=True, nullable=False)
    korisnicko_ime = db.Column(db.String(50), primary_key=True, nullable=False)
    lozinka =  db.Column(db.Text, nullable=False)
    tip_naloga = db.Column(db.String(15), nullable=False, default='TOURIST')
    rezervacije = db.relationship('Rezervacija', lazy = 'dynamic')
    aranzmani = db.relationship('Aranzman', lazy = 'dynamic', primaryjoin='Korisnik.korisnicko_ime==Aranzman.vodic')


# Klasa Aranzman
class Aranzman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opis = db.Column(db.Text, nullable=False)
    destinacija = db.Column(db.String(50), nullable=False)
    broj_mesta = db.Column(db.Integer, nullable=False)
    slobodna_mesta = db.Column(db.Integer, nullable=False)
    cena = db.Column(db.Float, nullable=False)
    pocetak = db.Column(db.DateTime, nullable=False)
    kraj = db.Column(db.DateTime, nullable=False)
    vodic = db.Column(db.String(50), db.ForeignKey('korisnik.korisnicko_ime', ondelete='CASCADE'), nullable=True)
    admin = db.Column(db.String(50), db.ForeignKey('korisnik.korisnicko_ime', ondelete='SET NULL'), nullable=False)
    rezervacije = db.relationship('Rezervacija', lazy = 'dynamic', cascade='all,delete')


# Klasa rezervacija
class Rezervacija(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aranzman = db.Column(db.Integer, db.ForeignKey('aranzman.id', ondelete='CASCADE'), nullable=False)
    korisnik = db.Column(db.String(50), db.ForeignKey('korisnik.korisnicko_ime', ondelete='CASCADE'), nullable=False)
    broj_mesta = db.Column(db.Integer, nullable=False)
    ukupna_cena = db.Column(db.Float, nullable=False)


# Klasa Zahtev za nadogradnju profila
class Zahtev(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    podnosilac = db.Column(db.String(15), db.ForeignKey('korisnik.korisnicko_ime', ondelete='CASCADE'), nullable=False)
    zeljeni_nalog = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=NA_CEKANJU)

# reset lozinke preko koda
class ResetLozinke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    podnosilac = db.Column(db.String(15), db.ForeignKey('korisnik.korisnicko_ime', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(24), nullable=False)
    nova_lozinka = db.Column(db.Text, nullable=False)


    
