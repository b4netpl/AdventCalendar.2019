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
