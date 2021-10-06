import datetime

def moze_li_otkazati(dt):
    date_format = '%Y-%m-%d'
    today = datetime.date.today()
    delta = dt.date() - today
    return True if delta.days >=5 else False