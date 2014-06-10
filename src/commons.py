'''
Created on Jun 6, 2014

@author: anroco
'''


def generate_token(secret_key=None, expiration=600, **kwargs):
    '''
    (str, int, **kwargs) -> str

    Permite generar un token_guest temporal en el cual se encapsularan y
    encriptaran los datos contenidos en el kwargs. Retorna un str con el
    token_guest con los datos encriptados. El secret_key es utilizado para
    el proceso de cifrado y descifrado del token. JSON Web Token (JWT)
    '''

    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

    token = Serializer(secret_key, expires_in=expiration)
    return token.dumps(kwargs)


def validate_token(token_user, secret_key=None):
    '''
    (str) -> dict

    Permite verificar si el token_guest es valido. En caso de ser valido
    retorna True, en caso de fallar la verificacion retorna False.
    JSON Web Token (JWT)
    '''

    from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

    token = Serializer(secret_key)
    try:
        token.loads(token_user)
    except:
        return False
    return True


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
