import pytest

from spewe.template import Template


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
    tpl = Template(content="Hello {{user.username}}")
    assert tpl.render(context) == "Hello cloking"
    tpl = Template(content="Hello {{user.title.capitalize}} {{user.username}}")
    assert tpl.render(context) == "Hello Mme cloking"
    tpl = Template(content="<span class='bio'>{{user.bio}}</span>")
    assert tpl.render(context) == "<span class='bio'>" + context['user'].bio() + "</span>"


def test_iteration(context):
    tpl = Template(content="<div>{{user.title.capitalize}} {{user.username}} liked the books below: <ul>{% loop books %}<li>{{item.title}} from {{item.author}}</li></ul></div>")
    assert tpl.render(context) == "<div>Mme cloking liked the books below: <ul><li>1984 from G. Orwell</li></ul></div><li>Animal Farm from G. Orwell</li></ul></div><li>Beloved from Toni Morison</li></ul></div><li>Roots from Alex Haley</li></ul></div><li>So Long A Letter from Mariame Ba</li></ul></div>"


def test_condition(context):
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
