'''
Created on Jun 6, 2014

@author: anroco
'''
import requests
import json
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
                                               next_url=next_url,
                                               data=request.args.get('data')))


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
                                nickname=user['nickname'], title='Profile'))
    import ast

    data = {'nickname': user['nickname']} if next_url == 'endpoints.home' \
            else ast.literal_eval(request.args.get('data'))
    return redirect(url_for(next_url, **data))


@guest_user
def profile(nickname):
    '''
    (str) -> flask.render_template

    Permite construir el perfil de un usuario para ser mostrado al usuario.
    Tambien permite la actualizacion del perfil del usuario. Retorna la
    renderizacion del perfil. Cuando la solicitud del recurso es por el metodo
    GET, se realiza la consulta del perfil del usuario tomando como criterio de
    busqueda el nickname ingresado. Si el metodo es POST se realiza la
    actualizacion del perfil del usuario que este en sesion activa.
    '''
    if request.method == 'GET':
        user_profile = user_by_nickname(nickname)
    else:
        user_profile = register_email_skills()
    return render_template('_profile.html', profile=user_profile,
                           title='Profile')


@login_required
def register_email_skills():
    '''
    (str) -> flask.redirect

    permite registrar el email y los skills del usuario, si el registro fue
    exitodso puede ser rederigido a uno de dos endpoints:
        * endpoints.home, si es la primera vez que se registra el email y los
        skills.
        * endpoints.profile, si el usuario ya ha registrado previamente esta
        informacion y esta realizano un proceso de actualizacion.
    '''
    user = session['user']

    #crear una lista con los skills definidos por el usuario
    skills = request.form.getlist('skill')

    #definir los datos para enviar la solicitud de registro de skills
    data = {'token_user': user['token_user'], 'key_user': user['key'],
            'jsonskills': json.dumps(skills)}
    result = requests.post(OxRESTful_resource.REGISTER_SKILLS, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        return 'error registrando los skills'

    #definir los datos para enviar la solicitud de registro de email
    data = {'token_user': user['token_user'],
            'email': request.form['email']}
    result = requests.put(OxRESTful_resource.REGISTER_EMAIL, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        return 'error registrando email'

    #actualizar los datos de sesion del usuario con los actualizados
    session['user'].update(result.json())
    if 'full_register' in session:
        session.pop('full_register')
        return redirect(url_for('endpoints.home',
                                nickname=user['nickname']))
    return result.json()


@guest_user
def home(nickname):
    '''
    (str) -> flask.render_template

    Permite cargar el historial de questions y answers que ha realizado el
    usuario, desde el momento en que se registro en la aplicacion organizadas
    cronologicamente.
    '''
    user = user_by_nickname(nickname)
    data = {'token_user': session['token_guest']}
    result = requests.get(OxRESTful_resource.QUESTION_ANSWER_BY_USER + \
                          user['key'], data=data)
    if result.status_code != 200:
        return 'error cargar historial usuario'
    return render_template('_home.html', home=result.json(), title='Home')


@login_required
def create_question():
    '''
    (str) -> flask.redirect

    Gestiona el proceso de creacion de una nueva pregunta por parte del usuario
    Si el metodo de consumo del recurso es GET realiza el renderizado de la
    vista questions Si el metodo de consumo es POST realiza el registro de la
    nueva pregunta en el sistema.
    '''
    if request.method == 'GET':
        return render_template('question.html')

    user = session['user']

    data_question = request.form.to_dict()
    add_data = {'skills': request.form.getlist('skills'), 'source': 'web',
                'key_user': user['key']}
    data_question.update(add_data)
    data = {'token_user': user['token_user'],
            'jsontimeline': json.dumps(data_question)}
    result = requests.post(OxRESTful_resource.CREATE_QUESTION, data=data)
    if result.status_code != 200:
        return 'error crear question'
    return redirect(url_for('endpoints.home', nickname=user['nickname']))


@login_required
def create_answer(question):
    '''
    (str) -> flask.redirect

    Gestiona el proceso de creacion de una respuesta por parte del usuario
    Si el metodo de consumo del recurso es GET realiza el renderizado de la
    vista answer. Si el metodo de consumo es POST realiza el registro de la
    nueva respuesta en el sistema.
    '''

    if request.method == 'GET':
        return render_template('_answer.html', question=question)

    user = session['user']
    data_question = request.form.to_dict()
    add_data = {'source': 'web', 'key_user': user['key'],
                'key_post_original': question}
    data_question.update(add_data)
    data = {'token_user': user['token_user'],
            'jsontimeline': json.dumps(data_question)}
    result = requests.post(OxRESTful_resource.CREATE_ANSWER, data=data)
    if result.status_code != 200:
        return 'error crear answer'
    return redirect(url_for('endpoints.home', nickname=user['nickname']))


@guest_user
def finderdown():
    '''
    () -> flask.redirect

    Gestiona el endpoints.finderdown, obtiene el valor de la variable *find*
    para ser pasada como parametro al endpoints.finder y ralizar la busqueda
    por skill.
    '''
    return redirect(url_for('endpoints.finder', find=request.args.get('find')))


@guest_user
def view_alone(question):
    '''
    (str) -> flask.redirect

    Permite mostrar un question con sus anwers. La variable *question* continen
    el hash_key de la pregunta a ser buscada y mostrada.
    '''

    data = {'token_user': session['token_guest']}
    result_qwa = requests.get(OxRESTful_resource.QUESTION_WIN_ANSWER + \
                              question, data=data)
    data['hash_key'] = question
    result_a = requests.get(OxRESTful_resource.QUESTION_ALL_ANSWER, data=data)
    if result_qwa.status_code != 200 and result_a.status_code != 200:
        return 'error al consultar la question y sus answers'
    data_result = result_qwa.json()
    questions = data_result['question']
    win_answers = data_result['winanswers']
    answers = result_a.json()
    return render_template('_show.html', questions=questions, answers=answers,
                            win_answers=win_answers, title='Show')


def user_by_nickname(nickname):
    '''
    (str) -> dict

    permite consultar un usuario teniendo como criterio de busqueda el nickname
    del usuario.
    '''
    data = {'token_user': session['token_guest']}
    result = requests.get(OxRESTful_resource.USER_BY_NICKNAME + nickname,
                          data=data)
    if result.status_code != 200:
        return 'error consultando por nickname'
    return result.json()


@guest_user
def temp(question):
    '''
    (str) -> flask.redirect

    '''
    pass
