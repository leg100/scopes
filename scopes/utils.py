
def flatten(items):
    """ Flatten nested list of any recursion. """

    for i in items:
        if isinstance(i, list):
            for ii in flatten(i):
                yield ii
        else:
            yield i
