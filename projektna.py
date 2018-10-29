import csv
import json
import os
import requests
import re
import sys


# definiratje URL glavne strani bolhe za oglase z mačkami
ranking_url = 'http://www.wtatennis.com/rankings/'
# mapa, v katero bomo shranili podatke
wta_directory = 'igralke'
# ime datoteke v katero bomo shranili glavno stran
frontpage_filename = "igralke_fp.html"
# ime CSV datoteke v katero bomo shranili podatke
csv_filename = "igralke.csv"


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

def shrani_frontpage():
    text = download_url_to_string(ranking_url)
    shrani_spletno_stran(text, frontpage_filename)
return None

def razbij_na_bloke(vsebina):
    '''Vsebino datoteke razdeli na bloke.'''
    rx = re.compile(r'<div about(.*?)<div class="rankings-block">',
                    re.DOTALL)
    igralka = re.findall(rx, vsebina)
    return igralka

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


