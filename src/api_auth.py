'''
Created on Jun 6, 2014

@author: anroco
'''

from functools import wraps
from flask import session, redirect, url_for, current_app, request
from flask_oauth import OAuth
from commons import (generate_token, validate_token, difference_timeUTCnow,
                     add_timeUTCnow)

#definicion de variables necesarias para realizar la autenticacion con twitter.
TW_CONSUMER_KEY = 'QbINcoPerlOi4Y4QD3wSjHJKp'
TW_CONSUMER_SECRET = 'ZBR4eNAo6KUK0gnZO2vm2JKLZdU4gh3DVbcnSibC42diBz1fiJ'
TW_NAME = 'restanroco'
TW_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TW_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TW_BASE_URL = 'https://api.twitter.com/1.1/'
TW_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authenticate'

#creacion del OAuth para la autenticacion con twitter
tw_oauth = OAuth().remote_app(name=TW_NAME,
                                base_url=TW_BASE_URL,
                                request_token_url=TW_REQUEST_TOKEN_URL,
                                access_token_url=TW_ACCESS_TOKEN_URL,
                                authorize_url=TW_AUTHORIZE_URL,
                                consumer_key=TW_CONSUMER_KEY,
                                consumer_secret=TW_CONSUMER_SECRET)


@tw_oauth.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')


def login_required(func):
    '''
    Injecta el proceso de validacion de un usuario. Si el usuario no ha
    inicionado sesion sera redirigido al endpoints.login, si el susuario ya
    inicio sesion pero no ha terminado de realizar el proceso de registro para
    que registre el email y los skills.
    '''

    @wraps(func)
    def decorated_login(*args, **kwargs):

        #valida si el usuario tiene una sesion activa
        if not ('user' in session and session['user'] and life_token_user()):
            return redirect(url_for('endpoints.login',
                            next_url=request.endpoint, data=kwargs))

        #verifica si el usuario ya termino de realizar el proceso de registro
        elif request.endpoint != 'endpoints.profile' and \
                'full_register' in session and not session['full_register']:
            return redirect(url_for('endpoints.profile',
                                    nickname=session['user']['nickname']))

        return func(*args, **kwargs)
    return decorated_login


def guest_user(func):
    '''
    Injecta el proceso de validacion de guest user. Permite definir un
    token_guest para que los usuarios puedan consumir recursos que no necesitan
    establecer una sesion previa.
    '''

    @wraps(func)
    def decorated_guest_user(*args, **kwargs):
        secret_key = current_app.config['SECRET_KEY_ANONYMOUS']

        if 'user' in session:
            life_token_user()

        #valida si existe y/o esta activo el token_guest
        if not 'token_guest' in session or \
                not validate_token(session['token_guest'], secret_key):
            session['token_guest'] = generate_token(secret_key)

        return func(*args, **kwargs)
    return decorated_guest_user


def life_token_user():
    '''
    () -> bool

    Verifica si el token_user es activo. Retorna False si el token_user ha
    expirado. El token_user se renueva si:

        * El usuario tiene actividad en la aplicacion
        * El token_user actual no ha expirado
        * El lifetime del token_user es menor a la mitad de
          OX_TOKEN_USER_LIFETIME

    El tiempo de renovacion se define en la variable OX_TOKEN_USER_LIFETIME
    definida en el config de la aplicacion.
    '''

    import requests
    from restful_resource import OxRESTful_resource

    timelife_token = current_app.config['OX_TOKEN_USER_LIFETIME']
    if 'timelife_token' in session['user']:
        user = session['user']
        timelife = difference_timeUTCnow(user['timelife_token'])
        min_renew_token = timelife_token / 900

        #verifica si el lifetime del token_user es mayor a la mitad del
        #OX_TOKEN_USER_LIFETIME, de ser verdadero el token_user no es renovado.
        if timelife >= timelife_token / min_renew_token:
            return True

        #verifica si el lifetime del token_user es menor a la mitad del
        #OX_TOKEN_USER_LIFETIME y si lifetime es mayor o igual a 0, de ser
        #verdadero el token_user es renovado.
        elif timelife < timelife_token / min_renew_token and timelife >= 0:
            data = {'token_user': user['token_user']}
            resp = requests.put(OxRESTful_resource.RENEW_TOKEN_USER, data=data)
            if resp.status_code == 200:
                import json
                user['token_user'] = json.loads(resp.text)
                user['timelife_token'] = add_timeUTCnow(timelife_token)
                session['user'] = user
                return True
        else:
            session.clear()
    return False
