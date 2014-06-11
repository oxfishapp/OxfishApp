'''
Created on Jun 6, 2014

@author: anroco
'''
import requests
import json
from flask import (current_app, url_for, request, render_template, session,
                    redirect)
from flask.ext.restful import marshal
from api_auth import tw_oauth, login_required, guest_user
from restful_resource import OxRESTful_resource
from views_formats import profile_user
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
        return redirect(url_for('endpoints.profile',
                                nickname=user['nickname']))

    return redirect(url_for(next_url, nickname=user['nickname']))


@guest_user
def profile(nickname):
    if not 'user' in session or session['user']['nickname'] != nickname:
        data = {'token_user': session['token_guest']}
        result = requests.get(OxRESTful_resource.USER_BY_NICKNAME + nickname,
                              data=data)
        if result.status_code != 200:
            return 'error consultando por nickname'
        data['hash_key'] = result.json()['hash_key']
    else:
        user = session['user']
        data = {'token_user': session['token_guest'],
                'hash_key': user['hash_key']}
    result = requests.get(OxRESTful_resource.USER_PROFILE, data=data)
    if result.status_code != 200:
        return 'error consultando perfil'
    result_data = marshal(result.json(), profile_user)
    return render_template('profile.html', data=result_data)


@login_required
def register_email_skills(nickname):
    user = session['user']

    #crear una lista con los skills definidos por el usuario
    skills = [v for k, v in request.form.iteritems() if k.startswith('skill_')]

    #definir los datos para enviar la solicitud de registro de skills
    data = {'token_user': user['token_user'], 'key_user': user['key'],
            'jsonskills': json.dumps(skills)}
    result = requests.post(OxRESTful_resource.REGISTER_SKILLS, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        return 'error registrando los skills'

    #definir los datos para enviar la solicitud de registro de email
    data = {'token_user': user['token_user'], 'email': request.form['email']}
    result = requests.put(OxRESTful_resource.REGISTER_EMAIL, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        return 'error registrando email'

    #actualizar los datos de sesion del usuario con los actualizados
    session['user'].update(result.json())
    if 'full_register' in session:
        session.pop('full_register')
        return redirect(url_for('endpoints.home', nickname=user['nickname']))
    return redirect(url_for('endpoints.profile', nickname=user['nickname']))


@login_required
def home(nickname):
    return render_template('layout_in.html')
