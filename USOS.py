import os
import re
import sys
from tkinter import Tk
import icalendar
import requests

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

instrukcja = f'{bcolors.OKGREEN}[INSTRUKCJA]{bcolors.ENDC}'
blad = f'{bcolors.FAIL}[BŁĄD]{bcolors.ENDC}'
ostrzezenie = f'{bcolors.WARNING}[OSTRZEŻENIE]{bcolors.ENDC}'
info = f'{bcolors.OKBLUE}[INFO]{bcolors.ENDC}'
def pobierzKalendarz():
    url = input(f'{instrukcja} Wklej URL swojego planu zajęć (przycisk eksportuj nad planem zajęć): ')
    try:
        print(f'{info} Pobieranie kalendarza')
        imp = requests.get(url).text

        print(f'{info} Tworzenie danych użytecznych')
        kalendarz = icalendar.Calendar.from_ical(imp)
        print(f'')
        return kalendarz

    except:
        print(f'{blad} Wystąpił błąd. Czy wprowadzony adres na pewno jest prawidłowy?')
        print(f'')
        return pobierzKalendarz()

def utworzSlownikPrzedmiotSkrot():
    przedmioty = {}
    print(f'{instrukcja} Przekopiuj całą swoją stronę "Grupy zajęciowe" (CTRL+A, CTRL+C)')
    input(f'{instrukcja} Po skopiowaniu wciśnij ENTER. {bcolors.UNDERLINE}UWAGA! NIE WKLEJAJ{bcolors.ENDC}')
    print(f'{info} Znajdowanie przedmiotów i kodów')
    try:
        print(f'{info} Pobieranie danych ze schowka')
        schowek = Tk().clipboard_get()

        print(f'{info} Tworzenie danych użytecznych')
        print()
        przekopiowanaStrona = schowek.splitlines()

        for linia in przekopiowanaStrona:

            if re.match(r'^(.*?) \[([^]]+)]$', linia):

                pelnaNazwaMatch = re.match(r'^(.*?) \[', linia)
                pelnaNazwa = pelnaNazwaMatch.group(1)
                kodMatch = re.match(r'.*-([A-Za-z]+)]', linia)

                if kodMatch:
                    kod = kodMatch.group(1)
                    print(f'{info} Znaleziono skrót: {bcolors.BOLD}{kod}{bcolors.ENDC} dla przedmiotu: {bcolors.BOLD}{pelnaNazwa}{bcolors.ENDC}')
                else:
                    print(f'{ostrzezenie} Nie udało się utworzyć skrótu dla przedmiotu: {bcolors.BOLD}{pelnaNazwa}{bcolors.ENDC}')
                    kod = input(f'{instrukcja} Podaj skrót tego przedmiotu: ')
                    print(f'{info} Utworzono skrót: {bcolors.BOLD}{kod}{bcolors.ENDC} dla przedmiotu: {bcolors.BOLD}{pelnaNazwa}{bcolors.ENDC}')
                przedmioty[kod] = pelnaNazwa

        return przedmioty
    except:
        print(f'{blad} Wystąpił błąd. Czy na pewno przekopiowano stronę "Grupy zajęciowe"?')
        return utworzSlownikPrzedmiotSkrot()
def zamienTytuly(slownik,kalendarz):

    print(f'{info} Zamienianie tytułów')
    events= [event for event in kalendarz.walk('VEVENT')]
    liczbaZajec = len(events)
    zamienianeZajecie = 1
    for event in kalendarz.walk('VEVENT'):
        print(f'{info} Zamienianie tytułów {zamienianeZajecie}/{liczbaZajec}')
        tytul=str(event["SUMMARY"])

        for skrot, rozwiniecie in slownik.items():
            tytul = tytul.replace(rozwiniecie,skrot)

        event["SUMMARY"]=tytul
        zamienianeZajecie+=1
    return kalendarz

def zamienBudynki(kalendarz):
    print()
    print(f'{info} Skracanie nazw budynków')
    events= [event for event in kalendarz.walk('VEVENT')]
    liczbaZajec = len(events)
    zamienianeZajecie = 1
    budynkiSlownik = {}
    for event in kalendarz.walk('VEVENT'):
        print(f'{info} Skracanie nazw budynków {zamienianeZajecie}/{liczbaZajec}')
        opis=str(event["DESCRIPTION"])
        opisList = opis.splitlines()
        if opisList[0] == '':
            lokalizacja = "Niepodano"
        else:
            sala = str(opisList[0].replace('Sala: ',''))
            budynek = opisList[1]

            if budynek in budynkiSlownik.keys():
                budynekSkrot=budynkiSlownik[budynek]

            else:
                print(f'{ostrzezenie} Nieznaleziono skróconej nazwy dla obiektu: {bcolors.BOLD}{budynek}{bcolors.ENDC}')
                print(f'{instrukcja} Wpisz pożądany skrót lub pozostaw puste i kliknij ENTER, aby niedodawać nazwy budynku do sali')
                budynekSkrot=input()
                budynkiSlownik[budynek]=budynekSkrot

            lokalizacja=sala+' '+budynekSkrot

        event['DESCRIPTION'] = ''
        event['LOCATION']=lokalizacja
        zamienianeZajecie+=1
    return kalendarz

def wybierzCzynnosc(kalendarz):
    print()
    print(f'{instrukcja} Wybierz czynność: ')
    print(f'1 - Zaimportuj od razu poprawiony USOS\'owy kalendarz do swojego kalendarza')
    print(f'2 - Zapisz plik kalendarza')
    print(f'0 - Zakończ program bez zapisywania')
    czynnosc = input(f'')

    if czynnosc == '0':
        print(f'{info} Zamykanie programu')
        sys.exit()
    if czynnosc == '1':
        print(f'{info} Tworzenie tymczasowego pliku .ics')
        try:
            out = open('out.ics','x')
            out.close()
            with open('out.ics', "wb") as file:
                file.write(kalendarz.to_ical())
        except FileExistsError:
            with open('out.ics', "wb") as file:
                file.write(kalendarz.to_ical())
        print(f'{info} Importowanie pliku do aplikacji kalendarza')
        os.system(f"open out.ics")
        input(f'{instrukcja} Po zakończonym imporcie kliknij ENTER')

        print(f'{info} Usuwanie tymczasowego pliku .ics')
        os.remove('out.ics')

        print(f'{info} Zamykanie programu')
        sys.exit()

    if czynnosc == '2':
        katalog = input(f'{instrukcja} Podaj katalog zapisu:')
        nazwa = input(f'{instrukcja} Podaj nazwę pliku: ')+'.ics'
        sciezka = f'{katalog}/{nazwa}'
        print(f'{info} Tworzenie pliku')
        try:
            out = open(sciezka,'x')
            out.close()
            with open(sciezka, "wb") as file:
                file.write(kalendarz.to_ical())
            print(f'{info} Utworzono plik w {sciezka}')
            print(f'')
            print(f'{info} Zamykanie programu')
            sys.exit()
        except Exception as e:
            print(f'{blad} Wystąpił błąd. {e}')
            wybierzCzynnosc(kalendarz)



    else:
        print(f'{blad} Niepoprawna czynność')
        print(f'')
        wybierzCzynnosc(kalendarz)

kalendarz = pobierzKalendarz()
slownik = utworzSlownikPrzedmiotSkrot()
print()
zamienTytuly(slownik,kalendarz)
zamienBudynki(kalendarz)
wybierzCzynnosc(kalendarz)