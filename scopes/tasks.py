from types import GeneratorType
from scopes import utils
from inspect import signature


tasks = []


def spout(obj):
    """ A normal or generator func with no dependency.  """
    def decorate(func):
        tasks.append(Spout(func, obj))
        return func

    return decorate


def bolt(obj, dep=None):
    """ A normal or generator func with dependency.  """
    def decorate(func):
        tasks.append(Bolt(func, obj, dep))
        return func
    return decorate


def builder(obj, dep, denominator=None):
    """ A func that modifies its obj without explicit return. """
    def decorate(func):
        tasks.append(Builder(func, obj, dep, denominator))
        return func
    return decorate


class Task(object):
    def __init__(self, func, obj, dep=None):
        self.func = func
        self.obj = obj
        self.dep = dep
        self.results = []

        self.validate()


    @property
    def name(self):
        return self.func.__name__


    def validate(self):
        self.validate_arity()


    def has_dependency(self):
        return bool(self.dep)


    def is_dependency(self, task):
        return self.dep.__call__(task.obj)


    def arity(self):
        return len(signature(self.func).parameters)


    def __repr__(self):
        return f"{type(self).__name__}:{self.func.__name__}:{self.obj}:{self.dep}"


class Spout(Task):
    def __init__(self, func, obj):
        super().__init__(func, obj)


    def is_dependency(self, _):
        """ A spout has no args, and therefore never has any dependencies """

        return False


    def validate_arity(self):
        if self.arity() > 0:
            raise Exception("A spout's function cannot have parameters")


    def run(self, args):
        """ A spout takes no args, so run func just once. Place the result
        into a list and flatten just in case a list has been returned as a
        result of enumerating a generator obj. """

        self.results = list(utils.flatten([self()]))


    def __call__(self):
        result = self.func()

        if isinstance(result, GeneratorType):
            return list(result)
        else:
            return result


class Bolt(Task):
    def __init__(self, func, obj, dep):
        super().__init__(func, obj, dep)


    def validate_arity(self):
        if self.arity() == 0:
            raise Exception("Bolt's function is missing its parameters")


    def run(self, args):
        """ A bolt only runs on each matching argument.
        The bolt may return a generator obj - which is converted into a list -
        so it needs to be flattened """

        for a in args:
            self.results.append(self(a))

        self.results = list(utils.flatten(self.results))


    def __call__(self, arg):
        result = self.func(arg)

        if isinstance(result, GeneratorType):
            return list(result)
        else:
            return result


class Builder(Task):
    def __init__(self, func, obj, dep, denominator=None):
        self.denominator = denominator

        super().__init__(func, obj, dep)


    def validate_arity(self):
        if self.arity() == 0:
            raise Exception("Builder's function is missing its parameters")


    def run(self, args):
        """ Run differently depending on whether a denominator has been
        specified: with a denominator, separate results according to args
        with a common denominator; without a denominator, just build one
        result obj from all args """

        if self.denominator is not None:
            _results = {}

            for a in args:
                d_val = a[self.denominator]
                _result = _results.setdefault(d_val, dict(self.obj))
                self(_result, a)

            self.results = list(_results.values())
        else:
            for a in args:
                self(self.obj, a)

            self.results = [self.obj]


    def __call__(self, obj, arg):
        self.func(obj, arg)
