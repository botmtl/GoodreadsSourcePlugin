from ast import literal_eval
from calibre_plugins.goodreads.config import plugin_prefs, STORE_NAME, KEY_IDENTIFIER_ORDER
from calibre.utils.logging import ThreadSafeLog

def get_goodreads_id_from_autocomplete(identifiers, timeout, log):
    # type: (dict, int, ThreadSafeLog) -> unicode or None
    """
    This method allows users to set their own priority for identifier based searches.
    The priority is set by changing the order of the key names in the preferences.
    :rtype: unicode or None
    :param timeout: int: timeout
    :param identifiers: dict: available identifiers for this book, will be filtered
    and sorted according to plugin_prefs[STORE_NAME][KEY_IDENTIFIER_ORDER]
    :param log: ThreadSafeLog: logging utility
    :return: unicode or None: a goodread_id or None
    """
    if not identifiers: identifiers={}
    try:
        #key_order is stored as a literal list of keys ['goodreads', 'amazon_ca', 'isbn']
        key_order = literal_eval(plugin_prefs[STORE_NAME][KEY_IDENTIFIER_ORDER])
        #for every key defined in plugin_prefs that exists this book's identifiers, create a
        #list(idenfifier_name:identifier_value) where identifier_name is in the same order as
        #key_order.
        keys = {unicode(identifier_name):unicode(identifiers[identifier_name]) for identifier_name in key_order if identifier_name in identifiers.keys()}
        log.info('Identifier keys will be used in this order to find an equivalent goodread_id:', keys)
    except:
        log.error('The plugin configuration is bad, and you should feel bad.')
        return None

    #for every key candidate
    for identifier_name,identifier_value in keys.items():
        #goodreads key is not found by using api
        if identifier_name == 'goodreads':
            return identifier_value
        try:
            result = autocomplete_api(identifier_value, timeout, log)
            goodreads_id = result.get('bookId')
            if goodreads_id:
                log.info('autocomplete found a match for ', {identifier_name:identifier_value}, ' ==> ', {'goodreads':goodreads_id})
                return goodreads_id
        except:
            #very likely the only exception here is a timeout
            pass
    return None


def autocomplete_api(search_terms, timeout, log):
    # type: (unicode, int, ThreadSafeLog) -> dict or None
    """
    :param timeout: int: urlopen will raise an exception
    (caught in get_goodreads_id_from_autocomplete) after this time
    :param search_terms: unicode: search term(s)
    :param log: ThreadSafeLog: logging utility
    :return: dict: a dictionnary representing the first book found by the api.
    """
    from urllib2 import urlopen
    import json
    search_terms = search_terms.strip()
    if search_terms is None: return None

    autocomplete_api_url = "https://www.goodreads.com/book/auto_complete?format=json&q="
    log.info('autocomplete url:', autocomplete_api_url, search_terms)
    response = urlopen(autocomplete_api_url + search_terms, timeout=timeout).read()
    if response:
        result = json.loads(response)
        if len(result) >= 1:
            return result[0]
    return None
