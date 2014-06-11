'''
Created on Jun 10, 2014

@author: anroco
'''

from flask import Blueprint
import views_users

endpoints = Blueprint('endpoints', __name__)

endpoints.add_url_rule('/login', 'login', views_users.login)
endpoints.add_url_rule('/getTokenTw', 'auth_twitter', views_users.auth_twitter)
endpoints.add_url_rule('/<string:nickname>/profile/register', 'register',
                       views_users.register_email_skills, methods=['POST'])
endpoints.add_url_rule('/<string:nickname>', 'home', views_users.home)
endpoints.add_url_rule('/<string:nickname>/profile', 'profile', views_users.profile)
