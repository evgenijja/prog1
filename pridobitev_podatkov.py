import requests
import re
import csv
import json
import sys
import os
import time
from pprint import pprint

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

vsebina = json.loads(open('rankings_real.json').read())
vsebina = str(vsebina)
vsebina = vsebina
#print(vsebina)

vzorec = re.compile(
    r'''{'rank': (?P<rank>\d+), 'move'.*?</span>', 'country':'''
    r''' '<span data-tooltip="(?P<drzava>.*?)'''
    r'''\" class=\"flag flag-icon flag-icon-.*?'''
    r'''href=\"#\" data-tooltip=.*?'''
    r'''href=\".player-profile.(?P<id>\d+).>(?P<ime>.*?)'''
    r'''<.a>', 'age': (?P<starost>\d+), 'points': (?P<tocke>\d+), 'tourn': (?P<odigrani_turnirji>\d+)}'''
    , re.DOTALL)

vzorec_za_igralko = re.compile(r'<div class="field__items"><div class="field__item even"><span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content=".*?T00:00:00\+00:00">'
                     r'(?P<datum_rojstva>.*?)</span></div></div></div>'
                     r'</div><div class="field field--name-field-height field--type-text field--label-hidden"><div class="field__items">'
                     r'<div class="field__item even">.*? <size>.*?'
                     r'-field-pro-year field--type-text field--label-hidden"><div class="field__items"><div class="field__item even">(?P<zacetek>.*?)</div></div></div><div class="field field--name-field-playhand field'
                     r'--type-text field--label-hidden"><div class="field__items"><div class="field__item even">(?P<roka>.*?)</div></div></div><div class="field field--name-field-residence field'
                     r'--type-text field--label-hidden"><div class="field__items"><div class="field__item even">.*?</div></div'
                     r'.*?'
                     r'</tr><tr class="odd"><td class="first">Prize Money</td><td class="ytd">(?P<letni_zasluzek>.*?)</td><td class="career last">(?P<karierni_zasluzek>.*?)</td>'
                     r'</tr><tr class="even"><td class="first">W/L - Singles</td><td class="ytd">(?P<letno_razmerje>.*?)</td>'
                     r'<td class="career last">(?P<karierno_razmerje>.*?)</td></tr></tbody></table></div></div></div></div></div>', re.DOTALL) 



def izloci_podatke(podatki_igralke):
    podatki_igralke = ujemanje.groupdict()
    podatki_igralke['ime'] = ' '.join(podatki_igralke['ime'].strip().split()[::-1])
    podatki_igralke['starost'] = int(podatki_igralke['starost'])
    podatki_igralke['id'] = int(podatki_igralke['id'])
    podatki_igralke['odigrani_turnirji'] = int(podatki_igralke['odigrani_turnirji'])
    podatki_igralke['tocke'] = int(podatki_igralke['tocke'])
    podatki_igralke['rank'] = int(podatki_igralke['rank'])
    return podatki_igralke

def izloci_podatke2(podatki):
    podatki = ujemanje.groupdict()
    podatki['roka'] = podatki['roka'].replace('-', ' ').replace('Right Handed', 'desna').replace('Left Handed', 'leva')
    podatki['letni_zasluzek'] = podatki['letni_zasluzek'].replace('$', '').replace(',', '').replace('.', '')
    podatki['karierni_zasluzek'] = podatki['karierni_zasluzek'].replace('$', '').replace(',', '').replace('.', '')
    return podatki

podatki_igralk = []
for ujemanje in vzorec.finditer(vsebina):
    podatki_igralke = izloci_podatke(ujemanje.groupdict())
    podatki_igralk.append(podatki_igralke)

igralka = []
for slovar in podatki_igralk:
    url = ('http://www.wtatennis.com/player-profile/{}'.format(slovar['id']))
    shrani_spletno_stran(url, 'zajeti-podatki/{}.html'.format(slovar['ime']))
    time.sleep(1)
    imena = ' '.join(slovar['ime'].strip().split())#[::-1]
    print(imena)
    vsebina = vsebina_datoteke('zajeti-podatki/{}.html'.format(imena))
    for ujemanje in vzorec_za_igralko.finditer(vsebina):
        podatki_za_igralko = izloci_podatke2(ujemanje.groupdict())
        igralka.append(podatki_za_igralko)

nov_seznam = []
for i in range(len(igralka)):
    a, b = podatki_igralk, igralka
    c = {**a[i], **b[i]}
    nov_seznam.append(c)


seznam_stvari = ['rank', 'id', 'ime', 'drzava', 'datum_rojstva', 'starost', 'roka', 'tocke', 'odigrani_turnirji', 'zacetek', 'letni_zasluzek', 'karierni_zasluzek', 'letno_razmerje', 'karierno_razmerje']
with open('seznam_igralk.csv', 'w', encoding="utf8") as csv_dat:
    writer = csv.DictWriter(csv_dat, seznam_stvari)
    writer.writeheader()
   # with open('seznam_igralk.json', 'w') as json_datoteka:
    for igralka in nov_seznam:
        writer.writerow(igralka)
            #json.dump(igralka, json_datoteka, indent=4, ensure_ascii=False)


                               
                            

    
