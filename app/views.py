from flask import Blueprint, jsonify, session, redirect, request, Response, json
from flask_mail import Message
from .models import Aranzman, Korisnik, Rezervacija, Zahtev, ResetLozinke
from .extensions import db, mail
from .security import hash_password, check_password, vrati_tip_naloga, generisi_reset_token, permisije
import datetime
from .utils import moze_li_modifikovati, sortiraj_datume, da_li_je_dostupan, moze_li_rezervisati, formatiraj_datum, vrati_konacnu_cenu, danas_plus_pet
from .constants import TOURIST, TRAVEL_GUIDE, ADMIN, ODOBREN, ODBIJEN, ASC, DESC
from .serializers import aranzman_schema, aranzmani_schema, korisnik_schema, korisnici_schema, rezervacija_schema, rezervacije_schema, zahtev_schema, zahtevi_schema, tourist_schema, tourists_schema, travel_guide_schema,travel_guides_schema, aranzman_detalji_schema, rezervacije_aranzmani_schema, aranzman_za_prijavljene_schema, aranzmani_za_prijavljene_schema

main = Blueprint('main', __name__)

date_format = '%Y-%m-%d'

ROWS_PER_PAGE = 5

# rute za neprijavljene korisnike

@main.route('/api/registracija', methods=['POST']) # registracija korisnika
def registracija():
    try:
        ime = request.json['ime']
        prezime = request.json['prezime']
        email = request.json['email']
        korisnicko_ime = request.json['korisnickoIme']
        lozinka = request.json['lozinka']
        potvrda_lozinke = request.json['potvrdaLozinke']
        zeljeni_nalog  = request.json['zeljeniNalog']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

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
    try:
        korisnicko_ime = request.json['korisnickoIme']
        lozinka = request.json['lozinka']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    postojeci_korisnik = Korisnik.query.filter_by(korisnicko_ime=korisnicko_ime).first()
    if postojeci_korisnik is None:
        return Response(json.dumps({'poruka': 'Korisnik ne postoji.'}), status=404, mimetype='application/json')
    
    if check_password(postojeci_korisnik.lozinka, lozinka) == False:
        return Response(json.dumps({'poruka': 'Uneta lozinka nije tacna.'}), status=400, mimetype='application/json')
    
    session['korisnik'] = korisnicko_ime
    return Response(json.dumps({'poruka': 'Prijava uspesna.'}), status=200, mimetype='application/json')


# odjava
@main.route("/api/odjava")
def odjava():
    session.pop('korisnik')
    return jsonify({'poruka': 'Odjava uspesna'})

# zahtev za reset lozinke
@main.route('/api/reset-lozinke', methods=['POST'])
def resetuj_lozinku():
    try:
        korisnik = request.json['korisnik']
        nova_lozinka = request.json['lozinka']
        potvrda_nove_lozinke = request.json['potvrdaLozinke']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    if nova_lozinka != potvrda_nove_lozinke:
        return Response(json.dumps({'poruka': 'Lozinke se ne poklapaju.'}), status=400, mimetype='application/json')

    postojeci_korisnik = Korisnik.query.filter((Korisnik.email == korisnik) | (Korisnik.korisnicko_ime == korisnik)).first()
    if postojeci_korisnik is None:
        return Response(json.dumps({'poruka': 'Korisnik ne postoji.'}), status=404, mimetype='application/json')

    
    nova_lozinka = hash_password(nova_lozinka)
    token = generisi_reset_token()

    poruka = Message('Zahtev za reset lozinke', sender='Agencija', recipients = [postojeci_korisnik.email])
    poruka.html = f"Postovani/a {korisnik}, potvrdite reset lozinke klikom na link: <a href='http://localhost:5000/api/reset-lozinke/{token}'>Resetuj lozinku</a>"
    mail.send(poruka)

    reset_lozinke = ResetLozinke(podnosilac=postojeci_korisnik.korisnicko_ime, nova_lozinka=nova_lozinka, token=token)
    db.session.add(reset_lozinke)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Poslat Vam je mejl za reset lozinke.'}), status=200, mimetype='application/json')

# reset preko tokena
@main.route('/api/reset-lozinke/<token>', methods=['GET'])
def resetuj_lozinku_tokenom(token):
    reset = ResetLozinke.query.filter_by(token=token).first()
    if reset is None:
        return Response(json.dumps({'poruka': 'Greska pri resetovanju lozinke. Nevazeci token.'}), status=400, mimetype='application/json')
    
    korisnik = Korisnik.query.get(reset.podnosilac)
    korisnik.lozinka = reset.nova_lozinka

    db.session.delete(reset)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Uspesno ste resetovali lozinku.'}), status=200, mimetype='application/json')

# -----------------------------------------------------------------------------------------------------

# TOURIST FUNKCIONALNOSTI

@main.route('/api/aranzmani', methods=['GET'])
def aranzmani():
    aranzmani = None
    stranica = request.args.get('stranica', 1, type = int) # paginacija
    sort = request.args.get('sort')
    if sort is None:
        sort = ASC

    aranzmani = Aranzman.query.order_by(Aranzman.pocetak.asc() if sort == ASC else Aranzman.pocetak.desc())
    
    # neprijavljeni korisnici vide samo osnovne stvari
    if session.get('korisnik') is None:
        rez = aranzmani.paginate(page=stranica, per_page=ROWS_PER_PAGE)
        ukupno = len(list(aranzmani))
        rezultat = aranzmani_schema.dump(rez.items)
        return jsonify({'aranzmani': rezultat, 'ukupno': ukupno})

    # TRAVEL GUIDE guide moze videti sve aranzmane
    
    if vrati_tip_naloga(session.get('korisnik')) == TOURIST:
        # za TORUIST uzmi aranzmane koje nije rezervisao
        rezervisani = Rezervacija.query.add_columns(Rezervacija.aranzman).filter_by(korisnik=session.get('korisnik'))
        rezervisani = list(x[1] for x in rezervisani)
        aranzmani = Aranzman.query.order_by(Aranzman.pocetak.asc() if sort == ASC else Aranzman.pocetak.desc())
        if rezervisani:
        # uzmi samo one do kojh ima makar 5 dana pre pocetka, i koji nisu rezervisani
            aranzmani = aranzmani.filter(Aranzman.id.notin_(rezervisani), Aranzman.pocetak > danas_plus_pet())

    destinacija = request.args.get('destinacija')
    pocetak = request.args.get('pocetak')
    kraj = request.args.get('kraj')    

    # proveri da li je zadata rec u destinaciji
    if destinacija is not None:
        aranzmani = aranzmani.filter(Aranzman.destinacija.like(f'%{destinacija}%'))
    # provera da li zadate datumske granice
    if pocetak is not None:
        aranzmani = aranzmani.filter(Aranzman.pocetak >= pocetak)
    if kraj is not None:
        aranzmani = aranzmani.filter(Aranzman.kraj <= kraj)

    rez = aranzmani.paginate(page=stranica, per_page=ROWS_PER_PAGE)
    ukupno = len(list(aranzmani))
    rezultat = aranzmani_za_prijavljene_schema.dump(rez.items)

    return jsonify({'aranzmani' :rezultat, 'ukupno': ukupno})

# detalji o aranzmanu
@main.route('/api/aranzmani/<id>')
@permisije(tip_naloga=TOURIST)
def aranzman_detaljnije(id):
    aranzman = Aranzman.query.get(id)
    rezultat = aranzman_za_prijavljene_schema.dump(aranzman)

    return jsonify(rezultat)

# korisnikove rezervacije i aranzmani
@main.route('/api/rezervacije', methods=['GET'])
@permisije(tip_naloga=TOURIST)
def moje_rezervacije():
    rezervacije = Rezervacija.query.filter_by(korisnik=session.get('korisnik')).join(Aranzman, Rezervacija.aranzman==Aranzman.id).add_columns(Rezervacija.id, Rezervacija.broj_mesta, Rezervacija.ukupna_cena, Aranzman.destinacija, Aranzman.opis, Aranzman.pocetak, Aranzman.kraj, Aranzman.vodic)
    # rezervacije i aranzmani join za datog korisnika 
    rezultat = rezervacije_aranzmani_schema.dump(rezervacije)

    return jsonify(rezultat)

# nova rezervacija
@main.route('/api/rezervacije', methods=['POST'])
@permisije(tip_naloga=TOURIST)
def nova_rezervacija():
    try:
        broj_mesta = request.json['broj_mesta']
        id_aranzmana = request.json['aranzman']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    aranzman = Aranzman.query.get(id_aranzmana)
    if moze_li_rezervisati(aranzman.pocetak) == False:
        return Response(json.dumps({'poruka': 'Odabrani aranzman pocinje za manje od 5 dana, nije ga moguce rezervisati.'}), status=400, mimetype='application/json')

    if aranzman.slobodna_mesta < broj_mesta:
        return Response(json.dumps({'poruka': 'Odabrani aranzman nema dovoljan broj slbodnih mesta za Vasu rezervaciju.'}), status=400, mimetype='application/json')
    
    ukupna_cena = vrati_konacnu_cenu(aranzman.cena, broj_mesta)
    rezervacija = Rezervacija(korisnik=session.get('korisnik'), aranzman=id_aranzmana, broj_mesta=broj_mesta, ukupna_cena=ukupna_cena)

    aranzman.slobodna_mesta -= broj_mesta

    db.session.add(rezervacija)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Uspesno ste izvrsili rezervaciju.'}), status=201, mimetype='application/json')

# profil korisnika 
@main.route('/api/profil', methods=['GET'])
@permisije(tip_naloga=TOURIST)
def moj_profil():
    korisnik = session.get('korisnik')
    profil = Korisnik.query.get(korisnik)

    rezultat = korisnik_schema.dump(profil)
    return jsonify(rezultat)

@main.route('/api/profil', methods=['PUT'])
@permisije(tip_naloga=TOURIST)
def izmena_profila():
    korisnik = session.get('korisnik')
    profil = Korisnik.query.get(korisnik)
    try:
        ime = request.json['ime']
        prezime = request.json['prezime']
        email = request.json['email']
        lozinka = request.json['lozinka'] # proveriti lozinku pre azuriranja podataka
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    if check_password(profil.lozinka, lozinka) == False:
        return Response(json.dumps({'poruka': 'Lozinka koju ste uneli nije ispravna.'}), status=400, mimetype='application/json')
    
    profil.ime = ime
    profil.prezime = prezime
    profil.email = email

    db.session.commit()

    return Response(json.dumps({'poruka': 'Uspesno ste azurirali profil'}), status=200, mimetype='application/json')

# zahtev za novi tip naloga
@main.route('/api/zahtevi', methods=['POST'])
@permisije(tip_naloga=TOURIST)
def zahtev_za_admina():
    podnosilac = session.get('korisnik')
    zeljeni_nalog = ADMIN if vrati_tip_naloga(podnosilac) == TRAVEL_GUIDE else TRAVEL_GUIDE
    zahtev = Zahtev(podnosilac=podnosilac, zeljeni_nalog=zeljeni_nalog)

    db.session.add(zahtev)
    db.session.commit()

    return Response(json.dumps({'poruka': f'Zahtev za nadogradnju profila u {zeljeni_nalog} uspesno poslat.'}), status=201, mimetype='application/json')


# ---------------------------------------------------------------------------------------------


# TRAVEL_GUIDE FUNKCIONALNOSTI


# aranzmani prijavljenog vodica
@main.route('/api/vodic/aranzmani/moji', methods=['GET'])
@permisije(tip_naloga=TRAVEL_GUIDE)
def aranzmani_vodica():
    aranzmani = Aranzman.query.filter_by(vodic=session.get('korisnik'))
    rezultat = aranzmani_schema.dump(aranzmani)
    return jsonify(rezultat)

# izmena opisa aranzmana
@main.route('/api/vodic/aranzmani/<id>', methods=['PUT'])
@permisije(tip_naloga=TRAVEL_GUIDE)
def uredi_opis_aranzmana(id):
    aranzman = Aranzman.query.get(id)
    if aranzman.vodic != session.get('korisnik'):
        return Response(json.dumps({'poruka': 'Ne mozete menjati opis aranzmana na kojem niste angazovani.'}), status=403, mimetype='application/json')

    if moze_li_modifikovati(aranzman.pocetak) == False:
        return Response(json.dumps({'prouka': 'Aranzman ne moze biti azuriran sada, najkasnije 5 dana pre pocetka.'}), status=400, mimetype='application/json')
    try:
        novi_opis = request.json["opis"]
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')
    aranzman.opis = novi_opis
    db.session.commit()

    return Response(json.dumps({'poruka': 'Uspesno ste izmenili opis aranzmana'}), status=200, mimetype='application/json')


# ---------------------------------------------------------------------------------------------


# ADMIN FUNKCIONALNOSTI

# dodavanje aranzmana
@main.route('/api/admin/aranzmani', methods=['POST'])
@permisije(tip_naloga=ADMIN)
def dodaj_aranzman():
    try:
        opis = request.json['opis']
        destinacija = request.json['destinacija']
        broj_mesta = request.json['brojMesta']
        cena = request.json['cena']
        pocetak = request.json['pocetak']
        kraj = request.json['kraj']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    pocetak = datetime.datetime.strptime(pocetak, date_format)
    kraj = datetime.datetime.strptime(kraj, date_format)

    aranzman = Aranzman(opis=opis, destinacija=destinacija, broj_mesta=broj_mesta, 
    slobodna_mesta=broj_mesta, cena=cena, pocetak=pocetak, kraj=kraj, admin=session.get('korisnik'))

    db.session.add(aranzman)
    db.session.commit()

    return Response(json.dumps({'poruka': 'Aranzman dodat.'}), status=201, mimetype='application/json')


# dodavanje vodica
@main.route('/api/admin/aranzmani/<id>/vodic', methods=['PUT'])
@permisije(tip_naloga=ADMIN)
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
@permisije(tip_naloga=ADMIN)
def azuriraj_aranzman(id):
    try:
        opis = request.json['opis']
        destinacija = request.json['destinacija']
        broj_mesta = request.json['brojMesta']
        cena = request.json['cena']
        pocetak = destinacija = request.json['pocetak']
        kraj = request.json['kraj']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    pocetak = datetime.datetime.strptime(pocetak, date_format)
    kraj = datetime.datetime.strptime(kraj, date_format)

    aranzman = Aranzman.query.get(id)

    if aranzman.admin != session.get('korisnik'):
        return Response(json.dumps({'poruka': 'Ne mozete menjati  aranzman koji niste napravili.'}), status=403, mimetype='application/json')

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
        return Response(json.dumps({'prouka': 'Aranzman ne moze biti azuriran sada, najkasnije 5 dana pre pocetka.'}), status=400, mimetype='application/json')

# brisanje/otkazivanje aranzmana
@main.route('/api/admin/aranzmani/<id>', methods=['DELETE'])
@permisije(tip_naloga=ADMIN)
def obrisi_aranzman(id):
    aranzman = Aranzman.query.get(id)

    if aranzman.admin != session.get('korisnik'):
        return Response(json.dumps({'poruka': 'Ne mozete obrisati aranzman koji niste napravili.'}), status=403, mimetype='application/json')

    if moze_li_modifikovati(aranzman.pocetak) == True:
        korisnici_rezervacije = Rezervacija.query.filter_by(aranzman=id).with_entities(Rezervacija.korisnik).all()
        korisnicka_imena = [x[0] for x in list(korisnici_rezervacije)]
        korisnici = Korisnik.query.filter(Korisnik.korisnicko_ime.in_(korisnicka_imena)).with_entities(Korisnik.email).all()
        mejlovi = [x[0] for x in list(korisnici)]
        if mejlovi:
            poruka = Message('Poruka o otkzivanju aranzmana za sve koji su rezervisali', sender='Agencija', recipients = mejlovi)
            poruka.body = f"Postovani, ovim putem Vam javljamo da je aranzman {aranzman.id} - {aranzman.destinacija} koji ste rezervisali otkazan. Sve najbolje, Agencija."
            mail.send(poruka)

        db.session.delete(aranzman)
        db.session.commit()
        return Response(json.dumps({}), status=204, mimetype='application/json')
    else:
        return Response(json.dumps({'prouka': 'Aranzman ne moze biti obrisan sada, najkasnije 5 dana pre pocetka.'}), status=400, mimetype='application/json')

# uvid u sve svoje kreirane aranzmane
@main.route('/api/admin/aranzmani/moji', methods=['GET'])
@permisije(tip_naloga=ADMIN)
def moji_aranzmani():
    aranzmani = Aranzman.query.filter_by(admin=session.get('korisnik'))
    rezultat = aranzmani_schema.dump(aranzmani)
    return jsonify(rezultat)

# uvid u sve aranzmane
@main.route('/api/admin/aranzmani', methods=['GET'])
@permisije(tip_naloga=ADMIN)
def svi_aranzmani():
    stranica = request.args.get('stranica')
    sort = request.args.get('sort')
    if sort is None:
        sort = ASC

    aranzmani = Aranzman.query.order_by(Aranzman.pocetak.asc() if sort == ASC else Aranzman.pocetak.desc()).paginate(page=stranica, per_page=ROWS_PER_PAGE).items
    rezultat = aranzmani_schema.dump(aranzmani)
    return jsonify(rezultat)

# uvid u detalje aranzmana
@main.route('/api/admin/aranzmani/<id>', methods=['GET'])
@permisije(tip_naloga=ADMIN)
def detalji_aranzmana(id):
    aranzman = Aranzman.query.get(id) # dodaj paginaciju, sortiranje
    rezultat = aranzman_detalji_schema.dump(aranzman)
    return jsonify(rezultat)


# adminov pregled svih korisnika sa filterom
@main.route('/api/admin/korisnici', methods=['GET'])
@permisije(tip_naloga=ADMIN)
def pregled_korisnika():
    stranica = request.args.get('stranica')
    sort = request.args.get('sort')
    if sort is None:
        sort = ASC
    tip = request.args.get('tip', TOURIST, type = str)
    # sort po prezimenu, moze po bilo cemu u sustini
    korisnici = Korisnik.query.order_by(Korisnik.prezime.asc() if sort == ASC else Korisnik.prezime.desc()).filter(Korisnik.tip_naloga==tip).paginate(page=stranica, per_page=ROWS_PER_PAGE).items
    rezultat = tourists_schema.dump(korisnici) if tip == TOURIST else travel_guides_schema.dump(korisnici)
    return jsonify(rezultat)


# pregled svih zahteva za nadogradnju profila
@main.route('/api/admin/zahtevi', methods=['GET'])
@permisije(tip_naloga=ADMIN)
def pregled_zahteva():
    zahtevi = Zahtev.query.all()
    rezultat = zahtevi_schema.dump(zahtevi)
    return jsonify(rezultat)

# odgovor na zahtev
# ovo je naravno moglo da se uradi na vise nacina, mozda samo preko parametara iz URL-a i slicno
@main.route('/api/admin/zahtevi/<id>', methods=['PUT'])
@permisije(tip_naloga=ADMIN)
def obradi_zahtev(id):
    try:
        odgovor = request.json['odgovor']
        komentar = request.json['komentar']
    except:
        return Response(json.dumps({'poruka': 'Uneti podaci nisu validni.'}), status=400, mimetype='application/json')

    zahtev = Zahtev.query.get(id)
    korisnik = Korisnik.query.filter_by(korisnicko_ime=zahtev.podnosilac).first()
    if odgovor == ODOBREN:
        zahtev.status = ODOBREN
        korisnik.tip_naloga = zahtev.zeljeni_nalog
        db.session.commit()
        poruka = Message('Zahtev za nadogradnju profila', sender='Agencija', recipients = [korisnik.email])
        poruka.body = f"Postovani/a {korisnik.ime} {korisnik.prezime}, ovim putem Vam javljamo da je Vas zahtev za nadogradnju profila prihvacen. Sve najbolje, Agencija"
        mail.send(poruka)
        return Response(json.dumps({'prouka': 'Zahtev za nadogradnju profila obradjen.'}), status=200, mimetype='application/json')
    else:
        # komentar ne sme biti prazan ako se odbija zahtev
        if not komentar:
            return Response(json.dumps({'prouka': 'Potrebno je da obrazlozite svoju odluku komentarom.'}), status=200, mimetype='application/json')
    
        zahtev.status = ODBIJEN
        db.session.commit()
        poruka = Message('Zahtev za nadogradnju profila', sender ='Agencija', recipients = [korisnik.email])
        poruka.body = f"Postovani/a ${korisnik.ime} {korisnik.prezime}, ovim putem Vam javljamo da je Vas zahtev za nadogradnju profila odbijen. {komentar}. Sve najbolje, Agencija"
        mail.send(poruka)
        return Response(json.dumps({'prouka': 'Zahtev za nadogradnju profila obradjen.'}), status=200, mimetype='application/json')
