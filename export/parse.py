from collections import OrderedDict
import six

from rthing.utils import rand_str
import re

indentation = 4

def _wrap(type_, name, text, indent, rstr=""):
    while rstr in text:
        rstr = rand_str(10)
    
    return u"{indent}{type} {name} {{{rstr}{{\n{text}\n{indent}}}{rstr}}}\n"\
        .format(type=type_, name=name, text=text, rstr=rstr, indent=" "*indent)

def _wrap_list(name, list_, indent):
    outs = ""
    for e in list_:
        outs += "\n"+encode(e, "{}-entry".format(name), indent+indentation)
    
    return _wrap("list", name, outs, indent)
    

def encode(value, key="root", indent=0):
    if isinstance(value, six.string_types) and "\n" in value:
        return _wrap("str", key, value, indent)
    elif isinstance(value, six.string_types):
        return u"{}str {}: {}\n".format(" "*indent, key, value)
    elif isinstance(value, bool):
        return u"{}bool {}: {}\n".format(" "*indent, key, value)
    elif isinstance(value, six.integer_types):
        return u"{}int {}: {}\n".format(" "*indent, key, value)
    elif isinstance(value, float):
        return u"{}float {}: {}\n".format(" "*indent, key, value)
    elif value is None:
        return u"{}none {}: None\n".format(" "*indent, key, value)
    else:
        try:
            # I want dicts and lists to be last
            outs = ""
            for dkey, dvalue in six.iteritems(value):
                outs += encode(dvalue, dkey, indent+indentation)
            return _wrap("dict", key, outs, indent)
        except AttributeError:
            try:
                for e in value:
                    pass
                return _wrap_list(key, value, indent)
            except TypeError:
                raise RuntimeError("{} is not a type that can be set to a text file".format(six.text_type(value)))


_single_expr = re.compile(r"^\s*(str|bool|int|float|none|comment)\s+([a-zA-Z0-9_-]+):\s*(.*)\s*$")
_block_open = re.compile(r"^\s*(str|list|dict|comment)\s+([a-zA-Z0-9_-]+)\s*?\{([a-z]+)\{\s*?$")
_block_close = re.compile(r"^\s*\}([a-z]+)\}\s*$")

def _cast(type_, value):
    if type_ == "str":
        return six.text_type(value)
    if type_ == "bool":
        return value.lower() in ("true", "yes", "1")
    if type_ == "int":
        if six.PY2:
            return long(value)
        else:
            return int(value)
    if type_ == "float":
        return float(value)
    if type_ == "comment":
        return ""
    if type_ == "none":
        return None
    
    return value


def _handle_child(parent_type, parent, child_type, child_name, child_value):
    if parent_type == "dict":
        parent[child_name] = _cast(child_type, child_value)
        return
    if parent_type == "list":
        parent.append(_cast(child_type, child_value))
        return
    
    raise RuntimeError("{} contains a child but does not support children".format(parent_type))


def decode(text):
    # Stack entries are in the format [obj, type, match, random string, name]
    stack = []
    
    lines = text.split("\n")
    
    for l in lines:
        close = _block_close.match(l)
        if close and close.group(1) == stack[-1][3]:
            # Block ended, pop it from the stack and attach it to its parent
            popped = stack.pop()
            
            if not stack:
                return popped[0]
            
            _handle_child(stack[-1][1], stack[-1][0], popped[1], popped[4], popped[0])
            continue
        
        if stack and stack[-1][1] == "str":
            # If the top of the stack is a string, just append it and ignore everything else
            if not stack[-1][0]:
                stack[-1][0] = stack[-1][0] + l
            else:
                stack[-1][0] = stack[-1][0] + "\n" + l
            continue
        
        expr = _single_expr.match(l)
        if expr:
            # Single expression
            if expr.group(1) == "comment":
                continue
            
            _handle_child(stack[-1][1], stack[-1][0], expr.group(1), expr.group(2), expr.group(3))
            
        
        open = _block_open.match(l)
        if open:
            # Open block, add it to the stack
            if open.group(1) == "comment":
                continue
            
            obj = None
            if open.group(1) == "str":
                obj = ""
            elif open.group(1) == "dict":
                obj = {}
            elif open.group(1) == "list":
                obj = []
            
            stack.append([obj, open.group(1), open, open.group(3), open.group(2)])
            continue
