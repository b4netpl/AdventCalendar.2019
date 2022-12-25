import json

from advencal.models import User, Day, Help


def test_app_group(runner_client):
    """
    GIVEN flask cli app
    WHEN flask cli is run without any args
    THEN init-data command group is visible among default command groups
    """
    assert 'init-data' in runner_client.invoke().output
    assert 'calendar' not in runner_client.invoke().output


def test_app_group_help(runner_client):
    """
    GIVEN flask cli app
    WHEN flask cli is run with init-data group arg
    THEN init-data command group help and contents are displayed
    """
    assert 'create-calendar' in runner_client.invoke(args='init-data').output


def test_create_user(runner_client, init_database):
    """
    GIVEN flask cli app
    WHEN create-user command is used
    THEN user with provided username and password is created
    """
    result = runner_client.invoke(args=[
            'init-data',
            'create-user',
            '--username',
            'clitest',
            '--password',
            'pass'
            ])
    assert result.output == ''
    assert User.check_username('clitest') is True

    user = User.query.filter_by(username='clitest').scalar()
    assert user.check_password('pass') is True


def test_create_user_double(runner_client, init_database, caplog):
    """
    GIVEN flask cli app
    WHEN create-user command is used with existing username
    THEN error message is written to log
    """
    runner_client.invoke(args=[
            'init-data',
            'create-user',
            '--username',
            'clitest',
            '--password',
            'pass'
            ])
    runner_client.invoke(args=[
            'init-data',
            'create-user',
            '--username',
            'clitest',
            '--password',
            'pass'
            ])
    assert 'UNIQUE constraint failed' in caplog.text


def test_create_calendar_noaction(runner_client, init_database):
    """
    GIVEN flask cli app
    WHEN create-calendar command is used with default No aswer to prompt
    THEN no data is changed in Day table
    """
    assert 'ERASE the calendar' in runner_client.invoke(args=[
            'init-data',
            'create-calendar'
            ], input='\n').output
    assert Day.get_day(1).day_no == 17


def test_create_calendar(runner_client, init_database):
    """
    GIVEN flask cli app
    WHEN empty-calendar command is used with --yes arg
    THEN initial data is written to Day table
    """
    runner_client.invoke(args=['init-data', 'create-calendar', '--yes'])
    assert Day.get_day(1).day_no == 17


def test_load_help_nofile(runner_client, init_database, fs):
    """
    GIVEN flask cli app
    WHEN load-help command is used and file is not loaded
    THEN error message is displayed
    """
    assert 'Error opening file. Data not changed.' \
        in runner_client.invoke(args=[
                'init-data',
                'load-help',
                'pl',
                '--yes'
                ]).output


def test_load_help(runner_client, init_database, fs):
    """
    GIVEN flask cli app
    WHEN load-help command is used
    THEN file contents are loaded to Help table
    """
    read_data = json.dumps([{
            "order": 1,
            "title": "Tytuł z pliku",
            "body": "Treść z pliku",
            "admin": False
            }])
    fs.create_file('./advencal/help/help.pl.json', contents=read_data)
    runner_client.invoke(args=['init-data', 'load-help', 'pl', '--yes'])
    helpitem = Help.get_helpitem(1)
    assert helpitem.title == 'Tytuł z pliku'


def test_save_help_nofile(runner_client, init_database, fs):
    """
    GIVEN flask cli app
    WHEN save-help command is used and file is not writable
    THEN error message is displayed
    """
    assert 'Error writing to file. Data not written.' \
        in runner_client.invoke(args=[
                'init-data',
                'save-help',
                'pl',
                '--yes'
                ]).output


def test_save_help(runner_client, init_database, fs):
    """
    GIVEN flask cli app
    WHEN save-help command is used
    THEN Help table contents are saved to file and file ends with newline
    """
    fs.create_file('./advencal/help/help.pl.json')
    runner_client.invoke(args=['init-data', 'save-help', 'pl', '--yes'])
    with open('./advencal/help/help.pl.json') as f:
        helpfile = f.read()
        assert 'Tytuł 1' in helpfile
        assert '\n' == helpfile[-1]
