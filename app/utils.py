import datetime
import time

date_format = '%Y-%m-%d'

# ogranicenje za modifikaciju aranzmana
def moze_li_modifikovati(dt):
    today = datetime.date.today()
    delta = dt.date() - today
    return True if delta.days >=5 else False

#sortiranje svih datuma vodica
def sortiraj_datume(datumi):
    return sorted(datumi)

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
        for i in range(0, len(datumi_aranzmana)-1):
            # ukoliko postoji vremenski period izmedju 2 aranzmana vodica takav da ispunjava uslov
            # da je kraj prvog pre pocetka ovog i pocetak drugog posle kraja ovog, onda je dostupan
            if datumi_aranzmana[i][1] < pocetak and datumi_aranzmana[i+1][0] > kraj:
                dostupan = True
                break
    return dostupan

