import requests
import re
import csv
import json
import sys
import os
import time

def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print('Shranjujem {} ...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)
            print('shranjeno!')

def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()

def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

def zapisi_json(objekt, ime_datoteke):
    '''Iz danega objekta ustvari JSON datoteko.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)


##############################################################################

with open('rankings.html') as datoteka:
    vsebina = datoteka.read()

vzorec = re.compile(
    r'''<tr><td class="rank footable-first-visible" headers="luxbox-ranking-col-rank" style="display: table-cell;">(?P<rank>\d+)</td>'''
    r'''<td class="move" headers="luxbox-ranking-col-move" style="display: table-cell;"><span><span class="move.*?">\S*</span>\d*</span></td>'''
    r'<td class="country" headers="luxbox-ranking-col-country" style="display: table-cell;">'
    r'<span data-tooltip=".*?" class="flag flag-icon flag-icon-.*?">'
    r'''<a href="http://www.wtatennis.com/rankings#" data-tooltip="(?P<drzava>.*?)">.*?'''
    r'''<td class="player" headers="luxbox-ranking-col-fullname" style="display: table-cell;"><div class="player-hidden">(?P<ime>.*?)</div>'''
    r'''<a href="http://www.wtatennis.com/player-profile/(?P<id>\d+)">.*?</a></td>'''
    r'''<td class="age" headers="luxbox-ranking-col-age" style="display: table-cell;">(?P<starost>\d+)</td>'''
    r'''<td class="points" headers="luxbox-ranking-col-points" style="display: table-cell;">(?P<tocke>\d+)</td>'''
    r'''<td class="played footable-last-visible" headers="luxbox-ranking-col-tourn" style="display: table-cell;">(?P<odigrani_turnirji>\d+)</td></tr>'''
    , re.DOTALL)

vzorec_za_igralko = re.compile(r'<div class="field__items"><div class="field__item even"><span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content=".*?T00:00:00\+00:00">'
                     r'(?P<datum_rojstva>.*?)</span></div></div></div>'
                     r'</div><div class="field field--name-field-height field--type-text field--label-hidden"><div class="field__items">'
                     r'<div class="field__item even">.*? <size>\((?P<visina>.*?).*?'
                     r'-field-pro-year field--type-text field--label-hidden"><div class="field__items"><div class="field__item even">(?P<zacetek>.*?)</div></div></div><div class="field field--name-field-playhand field'
                     r'--type-text field--label-hidden"><div class="field__items"><div class="field__item even">(?P<roka>.*?)</div></div></div><div class="field field--name-field-residence field'
                     r'--type-text field--label-hidden"><div class="field__items"><div class="field__item even">.*?</div></div'
                     r'.*?'
                     r'</tr><tr class="odd"><td class="first">Prize Money</td><td class="ytd">(?P<letni_zasluzek>.*?)</td><td class="career last">(?P<karierni_zasluzek>.*?)</td>'
                     r'</tr><tr class="even"><td class="first">W/L - Singles</td><td class="ytd">(?P<letno_razmerje>.*?)</td>'
                     r'<td class="career last">(?P<karierno_razmerje>.*?)</td></tr></tbody></table></div></div></div></div></div>', re.DOTALL) 

def izloci_podatke(podatki_igralke):
    podatki_igralke = ujemanje.groupdict()
    podatki_igralke['ime'] = podatki_igralke['ime'].strip()
    podatki_igralke['starost'] = int(podatki_igralke['starost'])
    podatki_igralke['id'] = int(podatki_igralke['id'])
    podatki_igralke['odigrani_turnirji'] = int(podatki_igralke['odigrani_turnirji'])
    podatki_igralke['tocke'] = int(podatki_igralke['tocke'])
    podatki_igralke['rank'] = int(podatki_igralke['rank'])
    return podatki_igralke

def izloci_podatke2(podatki):
    podatki = ujemanje.groupdict()
    podatki['roka'] = podatki['roka'].replace('-', ' ')
    return podatki

podatki_igralk = []
for ujemanje in vzorec.finditer(vsebina):
    podatki_igralke = izloci_podatke(ujemanje.groupdict())
    podatki_igralk.append(podatki_igralke)

igralka = []
for slovar in podatki_igralk:
    #url = ('http://www.wtatennis.com/player-profile/{}'.format(slovar['id']))
    #shrani_spletno_stran(url, 'zajeti-podatki/igralka-{}.html'.format(slovar['ime']))
    #time.sleep(1)
    vsebina = vsebina_datoteke('zajeti-podatki/igralka-{}.html'.format(slovar['ime']))
    for ujemanje in vzorec_za_igralko.finditer(vsebina):
        podatki_za_igralko = izloci_podatke2(ujemanje.groupdict())
        igralka.append(podatki_za_igralko)

nov_seznam = []
for i in range(len(igralka)):
    a, b = podatki_igralk, igralka
    c = {**a[i], **b[i]}
    nov_seznam.append(c)

seznam_stvari = ['rank', 'id', 'ime', 'drzava', 'datum_rojstva', 'starost', 'visina', 'roka', 'tocke', 'odigrani_turnirji', 'zacetek', 'letni_zasluzek', 'karierni_zasluzek', 'letno_razmerje', 'karierno_razmerje']
with open('seznam_igralk.csv', 'w', encoding="utf8") as csv_dat:
    writer = csv.DictWriter(csv_dat, seznam_stvari)
    writer.writeheader()
    with open('seznam_igralk.json', 'w') as json_datoteka:
        for igralka in nov_seznam:
            writer.writerow(igralka)
            json.dump(igralka, json_datoteka, indent=4, ensure_ascii=False)


                               
                            

    
