from flask import Blueprint, jsonify, session, redirect, request, Response, json
from flask_mail import Message
from .models import Aranzman, Korisnik,Rezervacija, Zahtev
from .extensions import db, mail
from .security import hash_password, check_password
import datetime
from .utils import moze_li_modifikovati, sortiraj_datume, da_li_je_dostupan
from .constants import TOURIST, TRAVEL_GUIDE, ADMIN, ODOBREN, ODBIJEN
from .serializers import aranzman_schema, aranzmani_schema, korisnik_schema, korisnici_schema, rezervacija_schema, rezervacije_schema, zahtev_schema, zahtevi_schema, tourist_schema, tourists_schema, travel_guide_schema,travel_guides_schema, aranzman_detalji_schema

main = Blueprint('main', __name__)

date_format = '%Y-%m-%d'

@main.route('/')
def main_index():
    svi_aranzmani_vodica = Aranzman.query.filter_by(vodic='Alex77np').with_entities(Aranzman.pocetak, Aranzman.kraj)
    datumi_vodica = sorted(list(svi_aranzmani_vodica))
    print(datumi_vodica)
    print(da_li_je_dostupan(datumi_vodica, datetime.datetime(2021,10,15,0,0), datetime.datetime(2021, 10,18,0,0)))
    return "hi"

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
        lozinka=lozinka, tip_naloga=TOURIST)

        db.session.add(korisnik)
        db.session.commit()

        session['korisnik'] = korisnicko_ime
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
    
    session['korisnik'] = korisnicko_ime
    return Response(json.dumps({'poruka': 'Prijava uspesna.'}), status=200, mimetype='application/json')


@main.route("/home")
def home():
  # check if the users exist or not
    if not session.get("korisnik"):
        # if not there in the session then redirect to the login page
        return redirect('/')
    return jsonify({'korisnik': session.get('korisnik')})

# odjava
@main.route("/odjava")
def logout():
    session.pop('korisnik')
    return jsonify({'poruka': 'Odjava uspesna'})


# ADMIN FUNKCIONALNOSTI

# dodavanje aranzmana
@main.route('/api/admin/aranzmani', methods=['POST'])
def dodaj_aranzman():
    opis = request.json['opis']
    destinacija = request.json['destinacija']
    broj_mesta = request.json['brojMesta']
    cena = request.json['cena']
    pocetak = request.json['pocetak']
    kraj = request.json['kraj']

    pocetak = datetime.datetime.strptime(pocetak, date_format)
    kraj = datetime.datetime.strptime(kraj, date_format)

    aranzman = Aranzman(opis=opis, destinacija=destinacija, broj_mesta=broj_mesta, 
    cena=cena, pocetak=pocetak, kraj=kraj, admin=session.get('korisnik'))

    db.session.add(aranzman)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Aranzman dodat.'}), status=201, mimetype='application/json')


# dodavanje vodica
@main.route('/api/admin/aranzmani/<id>/vodic', methods=['PUT'])
def angazuj_vodica(id):
    aranzman = Aranzman.query.get(id)
    vodic = request.json["vodic"]

    #provera da li je vodic slobodan
    svi_aranzmani_vodica = Aranzman.query.filter_by(vodic=vodic).with_entities(Aranzman.pocetak, Aranzman.kraj)
    datumi_vodica = sorted(list(svi_aranzmani_vodica))
    if da_li_je_dostupan(datumi_vodica, aranzman.pocetak, aranzman.kraj) == True:
        aranzman.vodic = vodic
        db.session.commit()
        return Response(json.dumps({'poruka': 'Uspesno ste dodali vodica za ovaj aranzman.'}), status=200, mimetype='application/json')

    return Response(json.dumps({'poruka': 'Odabrani vodic nije dostupan za ovaj aranzman.'}), status=400, mimetype='application/json')


# azuriranje aranzmana
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

    if moze_li_modifikovati(aranzman.pocetak) == True:
        aranzman.opis = opis
        aranzman.destinacija = destinacija
        aranzman.broj_mesta = broj_mesta
        aranzman.cena = cena
        aranzman.pocetak = pocetak
        aranzman.kraj = kraj

        db.session.commit()

        return Response(json.dumps({'poruka': 'Aranzman azuriran.'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'prouka': 'Aranzman ne moze biti azuriran'}), status=400, mimetype='application/json')

# brisanje/otkazivanje aranzmana
@main.route('/api/admin/aranzmani/<id>', methods=['DELETE'])
def obrisi_aranzman(id):
    aranzman = Aranzman.query.get(id)
    if moze_li_modifikovati(aranzman.pocetak) == True:
        korisnici_rezervacije = Rezervacija.query.filter_by(aranzman=id).with_entities(Rezervacija.korisnik).all()
        korisnicka_imena = [x[0] for x in list(korisnici_rezervacije)]
        korisnici = Korisnik.query.filter(Korisnik.korisnicko_ime.in_(korisnicka_imena)).with_entities(Korisnik.email).all()
        mejlovi = [x[0] for x in list(korisnici)]
        poruka = Message('Poruka o otkzivanju aranzmana za sve koji su rezervisali', sender='Agencija', recipients = mejlovi)
        poruka.body = f"Postovani, ovim putem Vam javljamo da aranzman koji ste rezervisali otkazan. Sve najbolje, Agencija."
        mail.send(poruka)

        db.session.delete(aranzman)
        db.session.commit()
        return Response(json.dumps({}), status=204, mimetype='application/json')
    else:
        return Response(json.dumps({'prouka': 'Aranzman ne moze biti obrisan'}), status=400, mimetype='application/json')

# uvid u sve svoje kreirane aranzmane
@main.route('/api/admin/aranzmani/moji', methods=['GET'])
def moji_aranzmani():
    aranzmani = Aranzman.query.filter_by(admin=session.get('korisnik'))
    rezultat = aranzmani_schema.dump(aranzmani)
    return jsonify(rezultat)

# uvid u sve aranzmane
@main.route('/api/admin/aranzmani', methods=['GET'])
def svi_aranzmani():
    aranzmani = Aranzman.query.all() # dodaj paginaciju, sortiranje
    rezultat = aranzmani_schema.dump(aranzmani)
    return jsonify(rezultat)

# uvid u detalje aranzmana
@main.route('/api/admin/aranzmani/<id>', methods=['GET'])
def detalji_aranzmana(id):
    aranzman = Aranzman.query.get(id) # dodaj paginaciju, sortiranje
    rezultat = aranzman_detalji_schema.dump(aranzman)
    return jsonify(rezultat)

# adminov pregled svih korisnika sa filterom

@main.route('/api/admin/korisnici', methods=['GET'])
def pregled_korisnika():
    tip = request.args.get('tip', 'TOURIST', type = str)
    korisnici = Korisnik.query.filter_by(tip_naloga=tip)
    rezultat = tourists_schema.dump(korisnici) if tip == 'TOURIST' else travel_guides_schema.dump(korisnici)
    return jsonify(rezultat)


# pregled svih zahteva za nadogradnju profila
# ovo je naravno moglo da se uradi na vise nacina, mozda samo preko parametara iz URL-a i slicno
@main.route('/api/admin/zahtevi', methods=['GET'])
def pregled_zahteva():
    zahtevi = Zahtev.query.all()
    rezultat = zahtevi_schema.dump(zahtevi)
    return jsonify(rezultat)

@main.route('/api/admin/zahtevi/<id>', methods=['PUT'])
def obradi_zahtev(id):
    odgovor = request.json['odgovor']
    zahtev = Zahtev.query.get(id)
    if odgovor == ODOBREN:
        zahtev.status = ODOBREN
        korisnik = Korisnik.query.filter_by(korisnicko_ime=zahtev.podnosilac).first()
        korisnik.tip_naloga = zahtev.zeljeni_nalog
        db.session.commit()
        poruka = Message('Zahtev za nadogradnju profila', sender='Agencija', recipients = [korisnik.email])
        poruka.body = f"Postovani/a {korisnik.ime} {korisnik.prezime}, ovim putem Vam javljamo da je vas zahtev za nadogradnju profila prihvacen. Sve najbolje, Agencija"
        mail.send(poruka)
        return Response(json.dumps({'prouka': 'Zahtev za nadogradnju profila obradjen.'}), status=200, mimetype='application/json')
    else:
        zahtev.status = ODBIJEN
        db.session.commit()
        poruka = Message('Zahtev za nadogradnju profila', sender ='Agencija', recipients = [korisnik.email])
        poruka.body = f"Postovani/a ${korisnik.ime} {korisnik.prezime}, ovim putem Vam javljamo da je vas zahtev za nadogradnju profila odbijen. Sve najbolje, Agencija"
        mail.send(poruka)
        return Response(json.dumps({'prouka': 'Zahtev za nadogradnju profila obradjen.'}), status=200, mimetype='application/json')
