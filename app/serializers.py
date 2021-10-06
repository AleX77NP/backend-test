from .extensions import ma

class KorisnikSchema(ma.Schema):
    class Meta:
        fields = ('ime', 'prezime', 'email', 'korisnicko_ime', 'tip_naloga')

korisnik_schema = KorisnikSchema()
korisnici_schema = KorisnikSchema(many=True)

class AranzmanSchema(ma.Schema):
    class Meta:
        fields = ('id', 'opis', 'destinacija', 'cena', 'broj_mesta', 'pocetak', 'kraj', 'vodic')

aranzman_schema = AranzmanSchema()
aranzmani_schema = AranzmanSchema(many=True)

class RezervacijaSchema(ma.Schema):
    class Meta:
        fields = ('id', 'aranzman', 'korisnik', 'broj_mesta', 'ukupna_cena')

rezervacija_schema = RezervacijaSchema()
rezervacije_schema = RezervacijaSchema(many=True)

class ZahtevSchema(ma.Schema):
    class Meta:
        fields = ('id', 'podnosilac', 'zeljeni_nalog')

zahtev_schema = ZahtevSchema()
zahtevi_schema = ZahtevSchema(many=True)