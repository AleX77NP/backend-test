from .extensions import ma
from marshmallow_sqlalchemy.fields import Nested, fields
from .models import Korisnik

class AranzmanSchema(ma.Schema):
    class Meta:
        fields = ('id', 'destinacija', 'cena', 'pocetak', 'kraj')

aranzman_schema = AranzmanSchema()
aranzmani_schema = AranzmanSchema(many=True)

class AranzmanZaPrijavljeneSchema(ma.Schema):
    class Meta:
        fields = ('id', 'destinacija', 'cena', 'pocetak', 'kraj', 'opis', 'vodic')

aranzman_za_prijavljene_schema = AranzmanZaPrijavljeneSchema()
aranzmani_za_prijavljene_schema = AranzmanZaPrijavljeneSchema(many=True)

# za admina
class AranzmanDetaljiSchema(ma.Schema):
    class Meta:
        fields = ('id', 'opis', 'destinacija', 'cena', 'pocetak', 'kraj', 'vodic', 'broj_mesta', 'slobodna_mesta')

aranzman_detalji_schema = AranzmanDetaljiSchema()

class RezervacijaSchema(ma.Schema):
    class Meta:
        fields = ('id', 'aranzman', 'korisnik', 'broj_mesta', 'ukupna_cena')

rezervacija_schema = RezervacijaSchema()
rezervacije_schema = RezervacijaSchema(many=True)

class ZahtevSchema(ma.Schema):
    class Meta:
        fields = ('id', 'podnosilac', 'zeljeni_nalog', 'status')

zahtev_schema = ZahtevSchema()
zahtevi_schema = ZahtevSchema(many=True)

class KorisnikSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.Int()
    ime = fields.Str()
    prezime = fields.Str()
    email = fields.Str()
    korisnicko_ime = fields.Str()

korisnik_schema = KorisnikSchema()
korisnici_schema = KorisnikSchema(many=True)

# ovde imamo odvojene seme za tourist i travel guide-a, za prvog uzimamo rezervacije, a za drugog angazmane

class TouristSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.Int()
    ime = fields.Str()
    prezime = fields.Str()
    email = fields.Str()
    korisnicko_ime = fields.Str()
    rezervacije = Nested(RezervacijaSchema, many=True)

tourist_schema = TouristSchema()
tourists_schema = TouristSchema(many=True)

class TravelGuideSchema(ma.Schema):
    class Meta:
        ordered = True
    id = fields.Int()
    ime = fields.Str()
    prezime = fields.Str()
    email = fields.Str()
    korisnicko_ime = fields.Str()
    aranzmani = Nested(AranzmanSchema, many=True)

travel_guide_schema = TravelGuideSchema()
travel_guides_schema = TravelGuideSchema(many=True)

# rezervacije i aranzmani join
class RezervacijaAranzmanSchema(ma.Schema):
    class Meta:
        ordered = True
    
    id = fields.Int()
    broj_mesta = fields.Int()
    ukupna_cena = fields.Float()
    destinacija = fields.Str()
    opis = fields.Str()
    pocetak = fields.DateTime()
    kraj = fields.DateTime()
    vodic = fields.Str()

rezervacije_aranzmani_schema = RezervacijaAranzmanSchema(many=True)


