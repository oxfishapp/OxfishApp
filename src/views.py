'''
Created on Jun 6, 2014

@author: anroco
'''
import requests
import json
import ast
from flask import (current_app, url_for, request, render_template, session,
                    redirect, jsonify, abort)
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
        abort(result.status_code)

    #almacenar los datos del usuario en un variable de sesion.
    user = result.json()
    timelife_token = current_app.config['OX_TOKEN_USER_LIFETIME']
    user['timelife_token'] = add_timeUTCnow(timelife_token)
    session['user'] = user

    #validar si el usuario culmino el proceso de registro.
    if result.status_code == 428:
        session['full_register'] = False
        return redirect(url_for('endpoints.profile',
                                nickname=user['nickname'], title='Profile'))
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
    from forms_fields import RegisterUserForm

    form_field = RegisterUserForm(request.form)
    if request.method == 'POST' and form_field.validate():
        return register_email_skills(form_field)
    profile = user_by_nickname(nickname)
    if request.method == 'POST':
        profile.update(form_field.data)
    return render_template('profile.html', title='Profile', form=form_field,
                           profile=profile)


@login_required
def register_email_skills(form_field):
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

    #definir los datos para enviar la solicitud de registro de skills
    data = {'token_user': user['token_user'], 'key_user': user['key'],
            'jsonskills': json.dumps(form_field.skills.data)}
    result = requests.post(OxRESTful_resource.REGISTER_SKILLS, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        abort(result.status_code)

    #definir los datos para enviar la solicitud de registro de email
    data = {'token_user': user['token_user'],
            'email': form_field.email.data}
    result = requests.put(OxRESTful_resource.REGISTER_EMAIL, data=data)

    #validar si el registro fue exitoso o no
    if result.status_code != 200:
        abort(result.status_code)

    #actualizar los datos de sesion del usuario con los actualizados
    user['skills'] = result.json()['skills']
    session['user'] = user
    if 'full_register' in session:
        session.pop('full_register')
        return redirect(url_for('endpoints.home',
                                nickname=user['nickname']))
    return render_template('profile.html', profile=result.json(),
                           title='Profile', form=form_field)


@guest_user
def home(nickname):
    '''
    (str) -> flask.render_template

    Permite cargar el historial de questions y answers que ha realizado el
    usuario, desde el momento en que se registro en la aplicacion organizadas
    cronologicamente.
    '''
    user = user_by_nickname(nickname)
    result_data = home_restful(key=user['key'])
    return render_template('home.html', home=result_data['data'], title='Home',
                           pagination=result_data['pagination'])


@login_required
def create_question():
    '''
    () -> flask.redirect

    Gestiona el proceso de creacion de una nueva pregunta por parte del usuario
    Si el metodo de consumo del recurso es GET realiza el renderizado de la
    vista questions Si el metodo de consumo es POST realiza el registro de la
    nueva pregunta en el sistema.
    '''
    from forms_fields import CreateQuestionForm

    form_field = CreateQuestionForm(request.form)

    if request.method == 'POST' and form_field.validate():
        user = session['user']
        data_question = form_field.data
        data_question.update({'source': 'web', 'key_user': user['key']})
        data = {'token_user': user['token_user'],
                'jsontimeline': json.dumps(data_question)}
        result = requests.post(OxRESTful_resource.CREATE_QUESTION, data=data)
        if result.status_code != 200:
            abort(result.status_code)
        data = {'token_user': user['token_user'], 'post': 1,
                'key_user': user['key']}
        result = requests.put(OxRESTful_resource.USER_SCORES, data=data)
        return redirect(url_for('endpoints.home', nickname=user['nickname']))

    return render_template('question.html', form=form_field)


@login_required
def create_answer():
    '''
    () -> flask.redirect

    Gestiona el proceso de creacion de una respuesta por parte del usuario
    Si el metodo de consumo del recurso es GET realiza el renderizado de la
    vista home. Si el metodo de consumo es POST realiza el registro de la
    nueva respuesta en el sistema.
    '''
    from forms_fields import CreateAnswerForm
    form_field = CreateAnswerForm(request.form)
    if form_field.validate():
        user = session['user']
        json_question = form_field.data
        json_question.update({'source': 'web', 'key_user': user['key']})
        data = {'token_user': user['token_user'],
                'jsontimeline': json.dumps(json_question)}
        result = requests.post(OxRESTful_resource.CREATE_ANSWER, data=data)
        if result.status_code != 200:
            abort(result.status_code)
        data = {'token_user': user['token_user'], 'answer': 1,
                'key_user': user['key']}
        result = requests.put(OxRESTful_resource.USER_SCORES, data=data)
        return redirect(url_for('endpoints.show',
                            question=form_field.data['key_post_original']))
    else:
        question = request.form['full_question']
        if question.startswith('_'):
            question = question[1:]
        else:
            form_field = CreateAnswerForm(request.form)
        question = ast.literal_eval(question)
        return render_template('answer.html', question=question,
                               form=form_field)


@guest_user
def finderdown():
    '''
    () -> flask.redirect

    Gestiona el endpoints.finderdown, obtiene el valor de la variable *find*
    para ser pasada como parametro al endpoints.finder y ralizar la busqueda
    por skill.
    '''
    find_by = request.args.get('find')
    if find_by:
        return redirect(url_for('endpoints.finder', find=find_by))
    abort(400)


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
    result_a = answers_restful(question=question)
    if result_qwa.status_code == 200 and result_a.status_code == 200:
        data_result = result_qwa.json()
        questions = data_result['question']
        win_answers = data_result['winanswers']
        answers = result_a.json()
        return render_template('show.html', questions=questions, title='Show',
                            answers=answers['data'], win_answers=win_answers,
                            pagination=answers['pagination'])
    abort(400)


@guest_user
def timeline_public():
    '''
    () -> flask.render_template

    Renderiza la vista timeline_public, consulta los questions que tienen al
    menos un answer, luego son mostrados al usuario en orden cronologico.
    '''
    result_data = timeline_restful()
    return render_template('timeline.html', timeline=result_data['data'],
                           pagination=result_data['pagination'],
                           title='Timeline Public')


@guest_user
def finder(find):
    '''
    (str) -> flask.render_template

    Permite realiza la busqueda de los questions asociados a un skill en
    particular, el parametro *find* contiene el nombre del skill a ser buscada.
    La lista de questions del skill buscado se muestran en la renderizacion de
    vista find_skill.
    '''
    result_data = find_restful(find=find)
    return render_template('find_skill.html', find_skill=result_data['data'],
                           pagination=result_data['pagination'],
                           title='Skill', found=find)


@login_required
def update_post():
    '''
    () -> flask.redirect

    Permite actualizar el estado de un answer asociado a un question, el asnwer
    puede alternar entre dos estados win answer y common answer. Se recibe el
    hash_key del question y answer seleccionada asi como el estado actual del
    answer a ser modificado. Redirige al endpoints.show para refrescar la vista
    '''

    from forms_fields import UpdatePostForm
    form_field = UpdatePostForm(request.form)

    if form_field.validate():
        user = session['user']
        new_data = form_field.data
        data = {'token_user': user['token_user'],
                'hash_key': new_data['question'],
                'jsontimeline': json.dumps({'state': new_data['state'],
                                       'hash_key_answer': new_data['answer']})}
        result = requests.put(OxRESTful_resource.UPDATE_POST, data=data)
        if result.status_code != 200:
            abort(result.status_code)
        data = {'token_user': user['token_user'],
                'key_user': form_field.data['key_user'],
                'w_answer': 1 if form_field.data['state'] else -1}
        result = requests.put(OxRESTful_resource.USER_SCORES, data=data)
        return redirect(url_for('endpoints.show',
                                question=new_data['question']))
    abort(400)


@login_required
def delete_post():
    '''
    () -> flask.redirect

    Elimina un question o answer, simpre que cumpla con los siguientes
    requerimientos:

        * Solo puede ser eliminada por el usuario que lo creo.
        * Un question solo puede ser eliminada si no tiene answers asociadas.
        * Un answer solo puede ser eliminada si no se ha marcado como win
          answer.

    si la eliminaion fue exitosa, se redirige al endpoints.home
    '''
    if request.method == 'POST':
        if 'full_post' in request.form:
            post = ast.literal_eval(request.form['full_post'])
            return render_template('delete.html', post=post)

        from forms_fields import DeletePostForm
        form_field = DeletePostForm(request.form)
        if form_field.validate():
            user = session['user']
            data = {'token_user': user['token_user'], 'key_user': user['key']}
            data['hash_key'] = form_field.data['hash_key']
            result = requests.delete(OxRESTful_resource.DELETE_QA, data=data)
            if result.status_code != 200:
                abort(result.status_code)
            data = {'token_user': user['token_user'], 'key_user': user['key'],
                    'post' if int(form_field.data['is_question']) else \
                                                                'answer': -1}
            result = requests.put(OxRESTful_resource.USER_SCORES, data=data)
        else:
            abort(400)
    return redirect(url_for('endpoints.home',
                            nickname=session['user']['nickname']))


@guest_user
def timeline_load():
    '''
    () -> flask.jsonify

    Permite realizar la carga del siguiente bloque de informacion para la vista
    timeline public.

    la variable pagination contiene la informacion necesaria para cargar el
    siguiente bloque de questions, este bloque de informacion es renderizado
    con el formato definido a_q_load_data.html.

    Finalizada la contruccion del html es retornado para ser mostrado al final
    de la pagina.
    '''
    pagination = request.json['pagination']
    if pagination:
        new_data = timeline_restful(request.json['pagination'])
        send_data = [render_template('a_q_load_data.html',
                                     data=new_data['data'])]
        return jsonify(lista=send_data, pagination=new_data['pagination'])
    return jsonify(lista=[], pagination=None)


@guest_user
def home_load():
    '''
    () -> flask.jsonify

    Permite realizar la carga del siguiente bloque de informacion para la vista
    home.

    la variable pagination contiene la informacion necesaria para cargar el
    siguiente bloque de questions y answers, este bloque de informacion es
    renderizado con el formato definido a_q_load_data.html.

    Finalizada la contruccion del html es retornado para ser mostrado al final
    de la pagina.
    '''
    pagination = request.json['pagination']
    if pagination:
        new_data = home_restful(request.json['pagination'])
        send_data = [render_template('a_q_load_data.html',
                                     data=new_data['data'])]
        return jsonify(lista=send_data, pagination=new_data['pagination'])
    return jsonify(lista=[], pagination=None)


@guest_user
def finder_load():
    '''
    () -> flask.jsonify

    Permite realizar la carga del siguiente bloque de informacion para la vista
    find.

    la variable pagination contiene la informacion necesaria para cargar el
    siguiente bloque de questions, este bloque de informacion es renderizado
    con el formato definido a_q_load_data.html.

    Finalizada la contruccion del html es retornado para ser mostrado al final
    de la pagina.
    '''
    pagination = request.json['pagination']
    if pagination:
        new_data = find_restful(request.json['pagination'])
        send_data = [render_template('a_q_load_data.html',
                                    data=new_data['data'])]
        return jsonify(lista=send_data, pagination=new_data['pagination'])
    return jsonify(lista=[], pagination=None)


@guest_user
def answers_load():
    '''
    () -> flask.jsonify

    Permite realizar la carga del siguiente bloque de informacion para la vista
    view alone.

    la variable pagination contiene la informacion necesaria para cargar el
    siguiente bloque de answers, este bloque de informacion es renderizado
    con el formato definido a_q_load_data.html.

    Finalizada la contruccion del html es retornado para ser mostrado al final
    de la pagina.
    '''
    pagination = request.json['pagination']
    if pagination:
        result = answers_restful(request.json['pagination'])
        new_data = result.json()
        send_data = [render_template('a_q_load_data.html',
                                     data=new_data['data'])]
        return jsonify(lista=send_data, pagination=new_data['pagination'])
    return jsonify(lista=[], pagination=None)


def logout():
    '''
    (str) -> flask.redirect

    Elimina la sesion activa que tiene un usuario, borra la variable de sesion
    user y redirige al endpoints.timeline.
    '''

    session.clear()
    return redirect(url_for('endpoints.timeline'))


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
        abort(result.status_code)
    return result.json()


def timeline_restful(pagination=None):
    '''
    (dict) -> dict

    Permite consultar los questions que se deben mostrar en el timeline public.
    Cuando pagination es None consulta las ultimas questions publicadas en el
    timeline, cuando es diferente a None se trae el siguiente bloque de
    questions el cual indica pagination.

    Retorna un dict con dos keys, el primero, data, el cual contiene la lista
    de questions y answers resultado de la busqueda y el segundo, pagination,
    el cual contine la informacion necesaria para realizar la carga del
    siguiente bloque en una nueva busqueda.
    '''
    data = {'token_user': session['token_guest'],
            'pagination': json.dumps(pagination) if pagination else "{}"}
    result = requests.get(OxRESTful_resource.PUBLIC_TIMELINE, data=data)
    if result.status_code != 200:
        abort(result.status_code)
    return result.json()


def home_restful(pagination=None, key=None):
    '''
    (dict, str) -> dict

    Permite consultar los questios y answers que se deben mostrar en el home.

    Si pagination es None, consulta los ultimos questions y answers realizados
    por un usuario, cuando pagination es diferente a None consulta el siguinete
    bloque de informacion.

    El parametro key indica el hash_key del usuario del cual se esta buscando
    el historial.

    Retorna un dict con dos keys, el primero, data, el cual contiene la lista
    de questions y answers resultado de la busqueda y el segundo, pagination,
    el cual contine la informacion necesaria para realizar la carga del
    siguiente bloque en una nueva busqueda.

    Nota: los parametros pagination y key no son usuados de forma simultanea,
    si son proporcionados en el mismo llamado de la funcion tiene prioridad
    pagination.
    '''
    data = {'token_user': session['token_guest'],
            'pagination': json.dumps(pagination) if pagination else "{}"}
    key_user = pagination['key_user'] if pagination else key
    result = requests.get(OxRESTful_resource.QUESTION_ANSWER_BY_USER \
                          + key_user,
                          data=data)
    if result.status_code != 200:
        abort(result.status_code)
    return result.json()


def find_restful(pagination=None, find=None):
    '''
    (dict, str) -> dict

    Permite consultar los questios asociadas al que se deben mostrar e.

    Si pagination es None consulta las primeras questions y answers de home,
    cuando es diferente a None se traen el siguinete bloque de questions el
    cual indica pagination.

    El parametro find es el nombre del skill que se esta buscando.

    Retorna un dict con dos keys, el primero, data, el cual contiene la lista
    de questions y answers resultado de la busqueda y el segundo, pagination,
    el cual contine la informacion necesaria para realizar la carga del
    siguiente bloque en una nueva busqueda.

    Nota: los parametros pagination y find no son usuados de forma simultanea,
    si son proporcionados en el mismo llamado de la funcion tiene prioridad
    pagination.
    '''
    data = {'token_user': session['token_guest'],
            'pagination': json.dumps(pagination) if pagination else "{}"}
    find = pagination['skill'][2:] if pagination else find
    result = requests.get(OxRESTful_resource.FINDER + find, data=data)
    if result.status_code != 200:
        abort(result.status_code)
    return result.json()


def answers_restful(pagination=None, question=None):
    '''
    (dict) -> dict

    permite consultar las answers que se deben mostrar en view alone.

    Si pagination es None, consulta las ultimas answers publicadas relacionadas
    a la question que se esta revisando, cuando es diferente a None se trae el
    siguinete bloque de answers el cual indica pagination.

    El parametro question es el hask_key del question que se esta revisando.

    Retorna un dict con dos keys, el primero, data, el cual contiene la lista
    de questions y answers resultado de la busqueda y el segundo, pagination,
    el cual contine la informacion necesaria para realizar la carga del
    siguiente bloque en una nueva busqueda.

    Nota: los parametros pagination y question no son usuados de forma
    simultanea, si son proporcionados en el mismo llamado de la funcion tiene
    prioridad pagination.
    '''
    question = pagination['key_post_original'] if pagination else question
    data = {'token_user': session['token_guest'], 'hash_key': question,
            'pagination': json.dumps(pagination) if pagination else "{}"}
    return requests.get(OxRESTful_resource.QUESTION_ALL_ANSWER, data=data)


@guest_user
def temp():
    '''
    (str) -> flask.redirect

    '''
    pass
