'''
Created on Jun 6, 2014

@author: anroco
'''

from flask.ext.restful.fields import Raw


class to_List(Raw):
    def format(self, value):
        """ (set) -> list
        retorna value como una lista (list).
        """
        return value if isinstance(value, list) else list(value)


def generate_token(secret_key=None, expiration=0, **kwargs):
    '''
    (str, int, **kwargs) -> str

    Permite generar un token_guest temporal en el cual se encapsularan y
    encriptaran los datos contenidos en el kwargs. Retorna un str con el
    token_guest con los datos encriptados. El secret_key es utilizado para
    el proceso de cifrado y descifrado del token. JSON Web Token (JWT)

    Si el secret_key es None, se toma SECRET_KEY_ANONYMOUS como valor por
    defecto, esta variable esta defenida en la configuracion de la aplicacion
    para el proceso de cifrado y descifrado del token.

    Si el expiration es 0, se toma OX_TOKEN_GUEST_USER_LIFETIME como valor por
    defecto, esta variable esta defenida en la configuracion de la aplicacion.
    '''
    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
    from flask import current_app

    if not expiration:
        expiration = current_app.config['OX_TOKEN_GUEST_USER_LIFETIME']
    if not secret_key:
        secret_key = current_app.config['SECRET_KEY_ANONYMOUS']
    token = Serializer(secret_key, expires_in=expiration)
    return token.dumps(kwargs)


def retrieve_token(token_user, secret_key=None):
    '''
    (str) -> dict

    Permite verificar si el token_guest es valido. En caso de ser valido
    retorna True, en caso de fallar la verificacion retorna False.
    JSON Web Token (JWT)

    Si el secret_key es None, se toma SECRET_KEY_ANONYMOUS como valor por
    defecto, esta variable esta defenida en la configuracion de la aplicacion
    para el proceso de cifrado y descifrado del token.
    '''

    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
    from flask import current_app

    if not secret_key:
        secret_key = current_app.config['SECRET_KEY_ANONYMOUS']

    token = Serializer(secret_key)
    try:
        return token.loads(token_user)
    except:
        return None


def add_timeUTCnow(add_seconds=0):
    """ (int) -> datetime.datetime

    retorna un datatime al cual se le agrego la cantidad de add_seconds a la
    hora UTC actual.
    """

    from datetime import datetime, timedelta

    return datetime.utcnow() + timedelta(seconds=add_seconds)


def difference_timeUTCnow(time):
    '''
    (datetime.datetime) -> int

    retorna la cantidad de segundos que hay entre la variable time y la hora
    UTC actual. Si la variable time es menor a la hora actual retorna un valor
    negativo.
    '''

    from datetime import datetime

    return (time - datetime.utcnow()).total_seconds()


def tokendict_to_multidict(token_dict):
    '''
    (srt) -> werkzeug.datastructures.MultiDict

    recibe el str del token que contiene los datos encriptados con estructura
    dict a ser recuperados y retornados en formato multidict.

    token_dict: es un str que contiene un dict ecriptado, ese dict son los
    datos a ser recuperados.
    '''
    from werkzeug.datastructures import MultiDict

    dict_data = retrieve_token(token_dict)
    if dict_data:
        multidict_data = MultiDict(dict_data.items())
    else:
        multidict_data = MultiDict()
    return multidict_data
