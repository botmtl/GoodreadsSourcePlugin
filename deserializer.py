
def deserializer(dictionary):
    """Recursively converts dictionary keys to strings."""
    if isinstance(dictionary, list):
        return list(dictionary)
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((unicode(k), deserializer(v))
                for k, v in dictionary.items())


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input