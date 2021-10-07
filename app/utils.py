import datetime
import time
from datetime import timedelta

date_format = '%Y-%m-%d'

# rad sa datumima

# ogranicenje za modifikaciju aranzmana
def moze_li_modifikovati(dt):
    today = datetime.date.today()
    delta = dt.date() - today
    return True if delta.days >=5 else False

# ogranicenje za rezervacije
def moze_li_rezervisati(dt):
    return (dt.date() - datetime.date.today()).days >= 5

# formatiranje datuma
def formatiraj_datum(dt):
    d = dt.strftime(date_format)
    return d

#sortiranje svih datuma vodica
def sortiraj_datume(datumi):
    return sorted(datumi)

def danas_plus_pet():
    return datetime.date.today() + timedelta(days=5)

# da li je vodic dostupan da vodi aranzman
def da_li_je_dostupan(datumi_aranzmana, pocetak, kraj):
    dostupan = False
    ravna = [d for sub in datumi_aranzmana for d in sub]
    sortirani = sortiraj_datume(ravna)
    print(sortirani)
    if pocetak > sortirani[-1] or kraj < sortirani[0]: 
    # ako je pocetak aranzmana veci datum od kraja poslednjeg u listi, 
    # ili je kraj istog raniji datum nego pocetak prvog gde je angazovan, vrati True
        dostupan = True
    else:
        for i in range(0, len(datumi_aranzmana)):
            # ukoliko postoji vremenski period izmedju 2 aranzmana vodica takav da ispunjava uslov
            # da je kraj prvog pre pocetka ovog i pocetak drugog posle kraja ovog, onda je dostupan
            if datumi_aranzmana[i][1] < pocetak and datumi_aranzmana[i+1][0] > kraj:
                dostupan = True
                break
    return dostupan

# ----------------------------------------------------------------------------------------

# popust za rezervaciju
def vrati_konacnu_cenu(cena, broj_mesta):
    return 3 * cena + (broj_mesta - 3) * (0.9 * cena) if broj_mesta > 3 else broj_mesta * cena

