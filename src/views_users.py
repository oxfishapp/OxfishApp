'''
Created on Jun 6, 2014

@author: anroco
'''
import requests
from flask import (current_app, url_for, request, render_template, session,
                    redirect)
from api_auth import tw_oauth, login_required, guest_user
from restful_resource import OxRESTful_resource
from commons import add_timeUTCnow


def login():
    '''
    () -> flask.redirect

    Gestiona el endpoints.login. Permite autenticar y obtener los tokens de
    usuario desde los servicios de twitter. define el endpoints.auth_twitter
    como callback para recibir la repuesta de autorizacion dada por twitter.
    '''

    next_url = request.args.get('next_url') or 'endpoints.home'
    return tw_oauth.authorize(callback=url_for('endpoints.auth_twitter',
                                               next_url=next_url))


@tw_oauth.authorized_handler
@guest_user
def auth_twitter(tw_resp):
    '''
    (dict) -> flask.redirect

    Gestiona el endpoints.auth_twitter. Recibe la respuesta de autorizacion de
    twitter, si la autorizacion del usuario es correcta tw_resp contien los
    tokens generados por twitter para el usuario.

    El usuario sera redirigido al enpoints.home si ya termino el proceso de
    registro, de lo contrario se lanzara la vista de registro para que culmine
    este proceso.
    '''

    #definir el endpoint al cual ser redirigido
    next_url = request.args.get('next_url') or \
                                url_for('endpoints.timelinepublic')
    data = {'token_user': session['token_guest'],
            'access_token': tw_resp['oauth_token'],
            'token_secret': tw_resp['oauth_token_secret']}

    #consumo del recurso login del Restful
    result = requests.post(OxRESTful_resource.LOGIN_USER, data=data)

    #validar el status_code de la respuesta
    if not result.status_code in [428, 200]:
        return "Error inicio sesion"

    #almacenar los datos del usuario en un variable de sesion.
    user = result.json()
    timelife_token = current_app.config['TOKEN_USER_LIFETIME']
    user['timelife_token'] = add_timeUTCnow(timelife_token)
    session['user'] = user

    #validar si el usuario culmino el proceso de registro.
    if result.status_code == 428:
        session['full_register'] = False
        return "terminar registro usuario"

    return redirect(url_for(next_url))


@login_required
def profile():
    user = session['user']
    data = {'token_user': user['token_user'],
            'hash_key': user['hash_key']}
    result = requests.get(OxRESTful_resource.USER_PROFILE, data=data)
    return render_template('profile.html')


@login_required
def register_email_skills():
    user = session['user']
    data = {'token_user': user['token_user'],
            'hash_key': user['hash_key']}
    result = requests.put(OxRESTful_resource.REGISTER_SKILLS, data=data)
    data = {'token_user': user['token_user'],
            }
    return "register email skills"





@login_required
def home():
    return render_template('layout_in.html')
