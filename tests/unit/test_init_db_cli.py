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


def test_create_user(runner_client, init_database, caplog):
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

    result = runner_client.invoke(args=[
            'init-data',
            'create-user',
            '--username',
            'clitest',
            '--password',
            'pass'
            ])
    assert 'UNIQUE constraint failed' in caplog.text
