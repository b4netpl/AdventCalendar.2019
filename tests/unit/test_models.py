from advencal.models import User, Day, Help


def test_new_user(new_user):
    """
    GIVEN a user Model
    WHEN a new User is created
    THEN check the username, password and rights are defined correctly
    """
    assert new_user.username == 'test'
    assert new_user.password != 'user'
    assert new_user.check_password('user') is True
    assert new_user.check_password('admin') is False
    assert new_user.admin is False


def test_new_admin(new_admin):
    """
    GIVEN a user Model
    WHEN a new User with admin rights is created
    THEN check the username, password and rights are defined correctly
    """
    assert new_admin.username == 'testadmin'
    assert new_admin.password != 'admin'
    assert new_admin.check_password('admin') is True
    assert new_admin.check_password('user') is False
    assert new_admin.admin is True


def test_user_repr(new_user, new_admin):
    """
    GIVEN a user Model
    WHEN a User object representation is called
    THEN check the username is correct in the representation
    """
    assert str(new_user) == '<User test>'
    assert str(new_admin) == '<User testadmin>'


def test_get_user(init_database):
    """
    GIVEN an existing User
    WHEN get_user() is called with existing User's id
    THEN object of type User is returned and it's id is equal to called
            function's arg
    """
    assert isinstance(User.get_user(1), User)
    assert User.get_user(1).id == 1


def test_check_username(init_database):
    """
    GIVEN a username string
    WHEN check_username() is called with a username
    THEN True is returned if user with that username exists in the database
            and False is returned if user with that username does not exist
            in the database
    """
    assert User.check_username('testadmin') is True
    assert User.check_username('test') is False


def test_day_repr(new_day):
    """
    GIVEN a day Model
    WHEN a Day object representation is called
    THEN check the day number is correct in the representation
    """
    assert str(new_day) == '<Day 5>'
    assert str(new_day) != '<Day 1>'


def test_get_day(init_database):
    """
    GIVEN an existing Day
    WHEN get_day() is called with existing Day's id
    THEN object of type Day is returned and it's id is equal to called
            function's arg
    """
    assert isinstance(Day.get_day(1), Day)
    assert Day.get_day(1).id == 1
    assert Day.get_day(1).day_no == 5


def test_help_repr(new_helpitem):
    """
    GIVEN a Help item Model
    WHEN a Help object representation is called
    THEN check the Help item title is correct in the representation
    """
    assert str(new_helpitem) == '<Help Tytuł>'
    assert str(new_helpitem) != '<Help Treść>'


def test_get_helpitem(init_database):
    """
    GIVEN an existing Help item
    WHEN get_helpitem() is called with existing Help item's id
    THEN object of type Help is returned and it's id is equal to called
            function's arg
    """
    assert isinstance(Help.get_helpitem(1), Help)
    assert Help.get_helpitem(1).id == 1
    assert Help.get_helpitem(1).title == 'Tytuł 1'


def test_get_max_order(init_database):
    """"
    GIVEN existing Help items
    WHEN get_max_order() is called with admin flag
    THEN correct max order of Help items for admin True or False is returned
    """
    assert Help.get_max_order(False) == 5
    assert Help.get_max_order(True) == 3
