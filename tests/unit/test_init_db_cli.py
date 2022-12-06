import json
import os.path

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
    assert 'empty-calendar' in runner_client.invoke(args='init-data').output


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
    assert 'UNIQUE constraint failed' in caplog.text


def test_empty_calendar_noaction(runner_client, init_database):
    """
    GIVEN flask cli app
    WHEN empty-calendar command is used with default No aswer to prompt
    THEN no data is changed in Day table
    """
    assert 'ERASE the calendar' in runner_client.invoke(args=[
            'init-data',
            'empty-calendar'
            ], input='\n').output
    assert Day.get_day(1).day_no == 5


def test_empty_calendar(runner_client, init_database):
    """
    GIVEN flask cli app
    WHEN empty-calendar command is used with --yes arg
    THEN initial data is written to Day table
    """
    runner_client.invoke(args=['init-data', 'empty-calendar', '--yes'])
    assert Day.get_day(1).day_no == 17


def test_help_load_nofile(runner_client, init_database, monkeypatch):
    """
    GIVEN flask cli app
    WHEN help-load command is used and file is not loaded
    THEN error message is displayed
    """
    def invalid_path(*args, **kwargs):
        return '/invalid/path'
    monkeypatch.setattr(os.path, 'join', invalid_path)
    assert 'Error opening file. Data not changed.' \
        in runner_client.invoke(args=[
                'init-data',
                'help-load',
                'pl',
                '--yes'
                ]).output


def test_help_load(runner_client, init_database, mocker):
    """
    GIVEN flask cli app
    WHEN help-load command is used
    THEN file contents are loaded to Help table
    """
    read_data = json.dumps([{
            "order": 1,
            "title": "Tytuł z pliku",
            "body": "Treść z pliku",
            "admin": False
            }])
    mocker.patch('builtins.open', mocker.mock_open(read_data=read_data))
    runner_client.invoke(args=['init-data', 'help-load', 'pl', '--yes'])
    helpitem = Help.get_helpitem(1)
    assert helpitem.title == 'Tytuł z pliku'


def test_help_save_nofile(runner_client, init_database, monkeypatch):
    """
    GIVEN flask cli app
    WHEN help-save command is used and file is not writable
    THEN error message is displayed
    """
    def invalid_path(*args, **kwargs):
        return '/invalid/path'
    monkeypatch.setattr(os.path, 'join', invalid_path)
    assert 'Error writing to file. Data not written.' \
        in runner_client.invoke(args=[
                'init-data',
                'help-save',
                'pl',
                '--yes'
                ]).output


def test_help_save(runner_client, init_database, mocker):
    """
    GIVEN flask cli app
    WHEN help-save command is used
    THEN Help table contents are saved to file and file ends with newline
    """
    m = mocker.patch('builtins.open', mocker.mock_open())
    runner_client.invoke(args=['init-data', 'help-save', 'pl', '--yes'])

    assert len(m().write.call_args_list) == 23
    m().write.assert_any_call('\n')
