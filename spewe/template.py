# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
import re


VAR_TOKEN_START, VAR_TOKEN_END = "{{", "}}"
BLOCK_TOKEN_START, BLOCK_TOKEN_END = "{%", "%}"
TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" % (
    VAR_TOKEN_START, VAR_TOKEN_END, BLOCK_TOKEN_START, BLOCK_TOKEN_END))
WHITESPACE = re.compile('\s+')

TEXT = 0
VAR = 1
BLOCK_START = 2
BLOCK_END = 3
DOT = '.'


class TemplateError(Exception):
    pass


class TemplateSyntaxError(TemplateError):
    pass


class TemplateContextError(TemplateError):
    pass


class LToken(object):

    def __init__(self, raw_content):
        self.raw_content = raw_content
        self.content = self.clean(raw_content)
        if raw_content.startswith(VAR_TOKEN_START):
            self.content_type = VAR
        elif self.content.startswith('end'):
            self.content_type = BLOCK_END
        elif raw_content.startswith(BLOCK_TOKEN_START):
            self.content_type = BLOCK_START
        else:
            self.content_type = TEXT

    def __repr__(self):
        return '<LToken:%s - %s>' % (self.content_type, self.content)

    def clean(self, raw_content):
        if raw_content.startswith((VAR_TOKEN_START, BLOCK_TOKEN_START)):
            return raw_content[2:-2].strip()
        return raw_content


class Node(object):

    def __init__(self, token=None):
        self.token = token
        self.children = []

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def render(self, context):
        rendered = ''
        if self.children:
            rendered = ''.join([str(child.render(context)) for child in self.children])
        return rendered


class ScopeNodeMixin(object):
    scope = True


class TextNode(Node):

    def render(self, context):
        return self.token.content


def get_possible_names(name):
    parts = name.split(DOT)
    length = len(parts)
    idx = length
    while idx > 0:
        yield idx, DOT.join(parts[:idx])
        idx -= 1


def attr_lookup(obj, attrs):
    if not attrs:
        return obj
    val = getattr(obj, attrs.pop(0))
    if not val:
        return None
    if callable(val):
        val = val()
    return attr_lookup(val, attrs)


def resolve(name, context):
    for klen, pkey in get_possible_names(name):
        if pkey in context:
            break
    else:
        raise TemplateContextError("%s does not exist in context" % name)

    if name == pkey:
        return context[pkey]
    attrs = name.split(DOT)
    attrs.remove(pkey)
    return attr_lookup(context[pkey], attrs)


class VarNode(Node):

    def render(self, context):
        content = self.token.content
        return resolve(content, context)


class LoopNode(Node, ScopeNodeMixin):

    def render(self, context):
        content = self.token.content
        items = content.strip().split()[-1]
        if items not in context:
            raise TemplateContextError("%s does not exist in context" % items)
        items = context[items]
        rendered = []
        for item in items:
            context['item'] = item
            rendered.append(''.join([str(child.render(context)) for child in self.children]))
        return ''.join(rendered)


class TemplateParser(object):

    def __init__(self, template):
        self.template = template
        self.tokens = self._tokenize()
        self.root = Node()

    def _tokenize(self):
        for token in TOKEN_REGEX.split(self.template):
            yield LToken(token)

    def _makenode(self, token):
        content = token.content
        content_type = token.content_type
        if content_type == VAR:
            return VarNode(token)
        if content_type == BLOCK_START:
            statement = content.split()[0]
            if statement == 'loop':
                return LoopNode(token)
        else:
            return TextNode(token)

    def _nodify(self):
        scopes = [self.root]  # rood node
        for token in self.tokens:
            parent_scope = scopes[-1]
            if token.content_type == BLOCK_END:
                scopes.pop()
                continue
            new_node = self._makenode(token)
            parent_scope.children.append(new_node)
            if token.content_type == BLOCK_START:
                scopes.append(new_node)
        return self.root

    def parse(self):
        return self._nodify()


class Template(object):

    def __init__(self, name=None, content=None, context=None):
        self.name = name
        self.content = content
        if not context:
            self.context = {}

    def load(self):
        with io.open(self.name, 'r') as fp:
            self.content = fp.read()
        return True

    @property
    def parser(self):
        return TemplateParser(self.content)

    def render(self, context=None):
        if not self.content and self.name:
            self.load()
        if context:
            self.context.update(context)
        return self.parser.parse().render(context)
