import pytest

from spewe.template import Template


class DataClass(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class User(DataClass):
    pass

    def bio(self):
        return "I'm %s and i will nail it" % self.username


class Book(DataClass):
    pass


@pytest.fixture
def context():
    attrs = {
        'uuid': 'abcd' * 8, 'username': 'cloking',
        'fname': 'chelsea', 'lname': 'loking',
        'title': 'mme'
    }
    context = dict(
        user=User(**attrs),
        books=[
            Book(author='G. Orwell', title='1984'),
            Book(author='G. Orwell', title='Animal Farm'),
            Book(author='Toni Morison', title='Beloved'),
            Book(author='Alex Haley', title='Roots'),
            Book(author='Mariame Ba', title='So Long A Letter'),
        ]
    )
    return context


def test_variables(context):
    tpl = Template(content="Hello {{user.username}}")
    assert tpl.render(context) == "Hello cloking"
    tpl = Template(content="Hello {{user.title.capitalize}} {{user.username}}")
    assert tpl.render(context) == "Hello Mme cloking"
    tpl = Template(content="<span class='bio'>{{user.bio}}</span>")
    assert tpl.render(context) == "<span class='bio'>" + context['user'].bio() + "</span>"
