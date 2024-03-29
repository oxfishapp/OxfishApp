'''
Created on Jun 6, 2014

@author: anroco
'''
import os


class OxRESTful_resource():

    #SERVER_NAME = 'http://localhost:5000/api/1.0'
    SERVER_NAME = os.environ.get('SERVER_NAME_RESTful')
    LOGIN_USER = SERVER_NAME + '/login'
    REGISTER_SKILLS = SERVER_NAME + '/auth/skills'
    REGISTER_EMAIL = SERVER_NAME + '/auth/register'
    USER_BY_KEY_USER = SERVER_NAME + '/user'
    USER_BY_NICKNAME = SERVER_NAME + '/user/'
    RENEW_TOKEN_USER = SERVER_NAME + '/auth/get_token'
    QUESTION_ANSWER_BY_USER = SERVER_NAME + '/home/'
    VIEW_ALONE_ASK = SERVER_NAME + '/home/'
    USER_SCORES = SERVER_NAME + '/auth/user'
    CREATE_QUESTION = SERVER_NAME + '/auth/post_q'
    CREATE_ANSWER = SERVER_NAME + '/auth/post_a'
    QUESTION_WIN_ANSWER = SERVER_NAME + '/post_qwa/'
    QUESTION_ALL_ANSWER = SERVER_NAME + '/allanswers'
    PUBLIC_TIMELINE = SERVER_NAME + '/publictimeline'
    FINDER = SERVER_NAME + '/findbyskill/'
    UPDATE_POST = SERVER_NAME + '/auth/update'
    DELETE_QA = SERVER_NAME + '/auth/delete'
