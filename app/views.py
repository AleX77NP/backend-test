from flask import Blueprint, jsonify, session, redirect, request, Response, json
from .models import Aranzman, Korisnik
from .extensions import db
from .security import hash_password, check_password
import datetime

main = Blueprint('main', __name__)

date_format = '%Y-%m-%d'

@main.route('/')
def main_index():
    return 'Hello World'

@main.route('/api/registracija', methods=['POST']) # registracija korisnika
def registracija():
    ime = request.json['ime']
    prezime = request.json['prezime']
    email = request.json['email']
    korisnicko_ime = request.json['korisnickoIme']
    lozinka = request.json['lozinka']
    potvrda_lozinke = request.json['potvrdaLozinke']
    zeljeni_nalog  = request.json['zeljeniNalog']

    if lozinka != potvrda_lozinke:
        return Response(json.dumps({'poruka': 'Lozinke se ne poklapaju.'}), status=400, mimetype='application/json')
    
    postojeci_korisnik = Korisnik.query.filter((Korisnik.email == email) | (Korisnik.korisnicko_ime == korisnicko_ime)).first()
    if postojeci_korisnik is not None:
        return Response(json.dumps({'poruka': 'Vec postoji nalog sa ovom email adresom ili korisnickim imenom'}), status=400, mimetype='application/json')

    try:
        lozinka = hash_password(lozinka)
        korisnik = Korisnik(ime=ime, prezime=prezime, email=email, korisnicko_ime=korisnicko_ime,
        lozinka=lozinka, tip_naloga='TOURIST')

        db.session.add(korisnik)
        db.session.commit()

        return Response(json.dumps({'poruka': 'Uspesna registracija.'}), status=201, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')


@main.route('/api/prijava', methods=['POST']) # prijava korisnika
def prijava():
    korisnicko_ime = request.json['korisnickoIme']
    lozinka = request.json['lozinka']

    postojeci_korisnik = Korisnik.query.filter_by(korisnicko_ime=korisnicko_ime).first()
    if postojeci_korisnik is None:
        return Response(json.dumps({'poruka': 'Korisnik ne postoji.'}), status=404, mimetype='application/json')
    
    if check_password(postojeci_korisnik.lozinka, lozinka) == False:
        return Response(json.dumps({'poruka': 'Uneta lozinka nije tacna.'}), status=400, mimetype='application/json')
    
    return Response(json.dumps({'poruka': 'Prijava uspesna.'}), status=200, mimetype='application/json')


@main.route('/api/aranzmani')
def aranzmani():
    aranzmani = Aranzman.query.all()
    return jsonify(aranzmani)


@main.route("/login/<korisnik>", methods=["POST", "GET"])
def login(korisnik):
    session['korisnik'] = korisnik
    return jsonify({'message': 'Log in'})

@main.route("/home")
def home():
  # check if the users exist or not
    if not session.get("korisnik"):
        # if not there in the session then redirect to the login page
        return redirect('/')
    return jsonify({'korisnik': session.get('korisnik')})

@main.route("/logout")
def logout():
    session.pop('korisnik')
    return jsonify({'message': 'Log out'})


# ADMIN funkcionalnosti 

@main.route('/api/admin/aranzmani', methods=['POST'])
def dodaj_aranzman():
    opis = request.json['opis']
    destinacija = request.json['destinacija']
    broj_mesta = request.json['brojMesta']
    cena = request.json['cena']
    pocetak = destinacija = request.json['pocetak']
    kraj = request.json['kraj']

    pocetak = datetime.datetime.strptime(pocetak, date_format)
    kraj = datetime.datetime.strptime(kraj, date_format)

    aranzman = Aranzman(opis=opis, destinacija=destinacija, broj_mesta=broj_mesta, 
    cena=cena, pocetak=pocetak, kraj=kraj)

    db.session.add(aranzman)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Aranzman dodat.'}), status=201, mimetype='application/json')

@main.route('/api/admin/aranzmani/<id>', methods=['PUT'])
def azuriraj_aranzman(id):
    opis = request.json['opis']
    destinacija = request.json['destinacija']
    broj_mesta = request.json['brojMesta']
    cena = request.json['cena']
    pocetak = destinacija = request.json['pocetak']
    kraj = request.json['kraj']

    pocetak = datetime.datetime.strptime(pocetak, date_format)
    kraj = datetime.datetime.strptime(kraj, date_format)

    aranzman = Aranzman.query.get(id)
    aranzman.opis = opis
    aranzman.destinacija = destinacija
    aranzman.broj_mesta = broj_mesta
    aranzman.cena = cena
    aranzman.pocetak = pocetak
    aranzman.kraj = kraj

    db.session.commit()

    return Response(json.dumps({'poruka': 'Aranzman azuriran.'}), status=200, mimetype='application/json')
    