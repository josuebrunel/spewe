import pytest

from spewe.template import Template
from spewe.exceptions import SpeweException


class DataClass(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class User(DataClass):

    def bio(self):
        return "I'm %s and i will nail it" % self.username


class Book(DataClass):

    def __repr__(self):
        return "<Book: %s - %s>" % (self.title, self.author)


@pytest.fixture
def context():
    attrs = {
        'uuid': 'abcd' * 8, 'username': 'cloking',
        'fname': 'chelsea', 'lname': 'loking',
        'title': 'mme', 'authenticated': True
    }
    context = dict(
        user=User(**attrs),
        books=[
            Book(author='G. Orwell', title='1984', price=20),
            Book(author='G. Orwell', title='Animal Farm', price=15),
            Book(author='Toni Morison', title='Beloved', price=15),
            Book(author='Alex Haley', title='Roots', price=20),
            Book(author='Mariame Ba', title='So Long A Letter', price=15),
        ]
    )
    return context


def test_variables(context):
    # test exception when variable doesn't exist
    with pytest.raises(SpeweException) as exc:
        tpl = Template(content="Hello {{user}}")
        tpl.render({})
    assert exc.value.args[0] == '<user> does not exist in context'
    tpl = Template(content="Hello {{user.username}}")
    assert tpl.render(context) == "Hello cloking"
    tpl = Template(content="Hello {{user.title.capitalize}} {{user.username}}")
    assert tpl.render(context) == "Hello Mme cloking"
    tpl = Template(content="<span class='bio'>{{user.bio}}</span>")
    assert tpl.render(context) == "<span class='bio'>" + context['user'].bio() + "</span>"


def test_iteration(context):
    # test iteration exception
    with pytest.raises(SpeweException) as exc:
        tpl = Template(content="{% loop books %}{{item}}{% endloop %}")
        tpl.render({})
    assert exc.value.args[0] == '<books> does not exist in context'
    tpl = Template(content="<div>{{user.title.capitalize}} {{user.username}} liked the books below: <ul>{% loop books %}<li>{{item.title}} from {{item.author}}</li></ul></div>")
    assert tpl.render(context) == "<div>Mme cloking liked the books below: <ul><li>1984 from G. Orwell</li></ul></div><li>Animal Farm from G. Orwell</li></ul></div><li>Beloved from Toni Morison</li></ul></div><li>Roots from Alex Haley</li></ul></div><li>So Long A Letter from Mariame Ba</li></ul></div>"
    # test iteration with dict items
    nums = {'one': 'un', 'two': 'deux'}
    tpl = Template(content="{% loop numbers %}<li><em>{{item[0]}}</em> is <em>{{item[1]}}</em> in french</li>{% endloop %}")
    rendered = tpl.render({'numbers': nums.items()})
    assert '<li><em>one</em> is <em>un</em> in french</li>' in rendered
    assert '<li><em>two</em> is <em>deux</em> in french</li>' in rendered


def test_condition(context):
    # test with invalid operator
    with pytest.raises(SpeweException) as exc:
        tpl = Template(content="{% if num >== 10 %}{{num}}{% endif %}")
        tpl.render({'num': 12})
    assert exc.value.args[0] == 'invalid syntax in statement: num >== 10'
    # test with invalid syntax
    with pytest.raises(SpeweException) as exc:
        tpl = Template(content="{% if nott authenticated %}{{error_message}}{% endif %}")
        tpl.render({'authenticated': True})
    assert exc.value.args[0] == 'invalid syntax in statement: nott authenticated'
    # test with non existant var in scope
    tpl = Template(content="{% if request.user %}Hello {{request.user.username}}{% endif %}")
    assert tpl.render({}) == ''

    context['user'].points = 1200
    tpl = Template(content="{% if user.points >= 1000 %}<div>User {{user.username}} is in beast mode!</div>{% endif %}")
    assert tpl.render(context) == "<div>User cloking is in beast mode!</div>"
    tpl = Template(content="{% if user.authenticated %}<div>Hello {{user.title}} {{user.username}}</div>{% endif %}")
    assert tpl.render(context) == "<div>Hello mme cloking</div>"
    tpl = Template(content="{% if user.authenticated %}<div>Hello {{user.title}} {{user.username}}</div>{% else %}<div>You need to sign in</div>{% endif %}")
    context['user'].authenticated = False
    assert tpl.render(context) == "<div>You need to sign in</div>"
    tpl = Template(content="{% loop books %}{% if item.title == '1984' %}<div>From {{item.author}} and costs ${{item.price}}</div>{% endif %}{% endloop %}")
    assert tpl.render(context) == "<div>From G. Orwell and costs $20</div>"
