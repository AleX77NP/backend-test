from marshmallow import Schema, fields, post_load, ValidationError, validates, validate

class RegistracijaKorisnikaSchema(Schema):
    ime = fields.Str(required=True)
    prezime = fields.Str(required=True)
    email = fields.Str(required=True)
    korisnicko_ime = fields.Str(required=True)
    lozinka = fields.Str(required=True)
    potvrda_lozinke = fields.Str(required=True)
    zeljeni_nalog = fields.Str(required=True)

    @validates('ime')
    def validate_ime(self, ime):
        if ime == '':
            raise ValidationError("Morate uneti ime!")
    @validates('prezime')
    def validate_prezime(self, prezime):
        if prezime == '':
            raise ValidationError("Morate uneti prezime!")
    @validates('email')
    def validate_email(self, email):
        if email == '':
            raise ValidationError("Morate uneti email!")
    @validates('korisnicko_ime')
    def validate_korisnicko_ime(self, korisnicko_ime):
        if korisnicko_ime == '':
            raise ValidationError("Morate uneti korisnicko ime!")
    @validates('lozinka')
    def validate_lozinka(self, lozinka):
        if lozinka == '':
            raise ValidationError("Morate uneti lozinku!")
    @validates('potvrda_lozinke')
    def validate_potvrda_lozinke(self, potvrda_lozinke):
        if potvrda_lozinke == '':
            raise ValidationError("Morate uneti potvrdu lozinke!")
    @validates('zeljeni_nalog')
    def validate_zeljeni_nalog(self, zeljeni_nalog):
        if zeljeni_nalog == '':
            raise ValidationError("Morate uneti zeljeni tip naloga!")
        