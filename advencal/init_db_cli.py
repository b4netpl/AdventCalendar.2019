import click

from flask.cli import AppGroup
from datetime import time
from advencal import app, db
from advencal.models import User, Day, DiscoveredDays, Help
from advencal.helpers import commit


init_data = AppGroup('init-data', short_help="Load data into db.")


@init_data.command("create-user")
@click.option('--username', prompt=True)
@click.password_option()
def create_user(username, password):
    """
    Create user with admin rights.
    """

    user = User(username=username, admin=True)
    user.set_password(password)
    db.session.add(user)

    commit(db.session)


@init_data.command("empty-calendar")
@click.confirmation_option(
        prompt='Are you sure you want to ERASE the calendar?'
        )
def empty_calendar():
    """
    Initialize empty calendar.

    This will erase all quests and answers from
    the calendar!!!

    All discovered days/answers will be erased
    as well!!!
    """

    Day.query.delete()
    DiscoveredDays.query.delete()

    commit(db.session)

    default_hour = time(hour=0, minute=0, second=0)

    db.session.add(Day(id=1, day_no=17, hour=default_hour))
    db.session.add(Day(id=2, day_no=2, hour=default_hour))
    db.session.add(Day(id=3, day_no=15, hour=default_hour))
    db.session.add(Day(id=4, day_no=8, hour=default_hour))
    db.session.add(Day(id=5, day_no=24, hour=default_hour))
    db.session.add(Day(id=6, day_no=9, hour=default_hour))
    db.session.add(Day(id=7, day_no=19, hour=default_hour))
    db.session.add(Day(id=8, day_no=6, hour=default_hour))
    db.session.add(Day(id=9, day_no=11, hour=default_hour))
    db.session.add(Day(id=10, day_no=22, hour=default_hour))
    db.session.add(Day(id=11, day_no=4, hour=default_hour))
    db.session.add(Day(id=12, day_no=14, hour=default_hour))
    db.session.add(Day(id=13, day_no=18, hour=default_hour))
    db.session.add(Day(id=14, day_no=5, hour=default_hour))
    db.session.add(Day(id=15, day_no=21, hour=default_hour))
    db.session.add(Day(id=16, day_no=7, hour=default_hour))
    db.session.add(Day(id=17, day_no=20, hour=default_hour))
    db.session.add(Day(id=18, day_no=13, hour=default_hour))
    db.session.add(Day(id=19, day_no=10, hour=default_hour))
    db.session.add(Day(id=20, day_no=1, hour=default_hour))
    db.session.add(Day(id=21, day_no=23, hour=default_hour))
    db.session.add(Day(id=22, day_no=16, hour=default_hour))
    db.session.add(Day(id=23, day_no=3, hour=default_hour))
    db.session.add(Day(id=24, day_no=12, hour=default_hour))

    commit(db.session)


@init_data.command("help-data")
@click.argument(
        'language',
        type=click.Choice(['pl', 'en'], case_sensitive=False)
        )
@click.confirmation_option(
        prompt='Are you sure you want to replace contents of Help section?'
        )
def help_data(language):
    """
    Add Help contents in <language>.

    This will erase current contents of Help section.
    """

    if language == 'pl':

        Help.query.delete()
        commit(db.session)

        db.session.add(Help(
                order=1,
                title='Jak działa kalendarz?',
                body='Kalendarz składa się z 24 pól, które będziesz odkrywać codziennie po jednym, aby na koniec zobaczyć finałowe zdjęcie i... niespodziankę! Jeśli w zabawie bierze udział więcej niż jedna osoba, każda uczestniczka zabawy dostaje swój własny login i hasło i rozwiązuje kalendarz samodzielnie.',
                admin=False
        ))
        db.session.add(Help(
                order=2,
                title='Co się stanie po kliknięciu na pole z numerkiem?',
                body='Jeśli dzień grudnia jest zgodny z numerkiem, po kliknięciu pojawi się zadanie.',
                admin=False
        ))

        # admin help
        db.session.add(Help(
                order=1,
                title='Jak dodać nowego użytkownika?',
                body='<p>Z kolorowego paska z nagłówkami na górze strony wybierasz menu Użytkownicy. Pojawi się strona z ramką Dodaj użytkownika. W polu „Login" wpisujesz dowolny login bez spacji (np. imię). Tym loginem użytkownik będzie się logował do kalendarza.'
                '<p>Jeśli zaznaczysz opcję „Podaj hasło", to musisz je wpisać w pole tekstowe „Hasło".'
                '<p>Jeśli zaznaczysz opcję „Wygeneruj losowe hasło", to system sam utworzy hasło.'
                '<p>Po kliknięciu w zielony przycisk „Dodaj użytkownika" konto zostanie założone. Wyświetli się komunikat potwierdzający. Najlepiej skopiować myszką treść z ramki na dole tego komunikatu i wysłać mailem użytkownikowi (będzie tam login, hasło i adres strony). Można też skopiować samo hasło zielonym przyciskiem "Skopiuj do schowka".',
                admin=True
        ))

        db.session.add(Help(
                order=2,
                title='Jak usunąć użytkownika?',
                body='Z kolorowego paska z nagłówkami na górze strony wybierasz menu Użytkownicy. Na dole strony w ramce "Zarządzaj użytkownikami" jest lista wszystkich założonych użytkowników. Wystarczy kliknąć "Usuń" przy wybranym użytkowniku. Uwaga! Ostrożnie - tej operacji nie da się cofnąć! (Przy użytkownikach z prawami administratora nie ma takiej opcji, prosimy o kontakt na adres bb@b4.net.pl).',
                admin=True
        ))

        commit(db.session)

    else:
        click.echo(
                'Language '
                + language
                + ' not found! No data were changed.'
                )


app.cli.add_command(init_data)
