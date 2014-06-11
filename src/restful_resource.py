'''
Created on Jun 6, 2014

@author: anroco
'''


class OxRESTful_resource():

    SERVER_NAME = 'http://localhost:5000'
    LOGIN_USER = SERVER_NAME + '/api/1.0/login'
    REGISTER_SKILLS = SERVER_NAME + '/api/1.0/auth/skills'
    REGISTER_EMAIL = SERVER_NAME + '/api/1.0/auth/register'
    USER_PROFILE = SERVER_NAME + '/api/1.0/user'
    USER_BY_NICKNAME = SERVER_NAME + '/api/1.0/user/'
    RENEW_TOKEN_USER = SERVER_NAME + '/api/1.0/auth/get_token'
