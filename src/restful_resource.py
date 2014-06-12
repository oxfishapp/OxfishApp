'''
Created on Jun 6, 2014

@author: anroco
'''


class OxRESTful_resource():

    SERVER_NAME = 'http://localhost:5000/api/1.0'
    LOGIN_USER = SERVER_NAME + '/login'
    REGISTER_SKILLS = SERVER_NAME + '/auth/skills'
    REGISTER_EMAIL = SERVER_NAME + '/auth/register'
    USER_BY_KEY_USER = SERVER_NAME + '/user'
    USER_BY_NICKNAME = SERVER_NAME + '/user/'
    RENEW_TOKEN_USER = SERVER_NAME + '/auth/get_token'
    QUESTION_ANSWER_BY_USER = SERVER_NAME + '/home/'
    VIEW_ALONE_ASK = SERVER_NAME + '/home/'
    CREATE_QUESTION = SERVER_NAME + '/auth/post_q'
