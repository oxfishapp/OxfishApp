'''
Created on Jun 10, 2014

@author: anroco
'''

from flask import Blueprint
import views_users

endpoints = Blueprint('endpoints', __name__)

endpoints.add_url_rule('/login', 'login', views_users.login)
endpoints.add_url_rule('/getTokenTw', 'auth_twitter', views_users.auth_twitter)
endpoints.add_url_rule('/<string:nickname>', 'home', views_users.home)
endpoints.add_url_rule('/<string:nickname>/profile', 'profile',
                       views_users.profile, methods=['GET', 'POST'])
endpoints.add_url_rule('/<string:nickname>/ask', 'ask',
                       views_users.create_question, methods=['GET', 'POST'])
endpoints.add_url_rule('/ask/<string:question>', 'show',
                       views_users.view_alone)
#timeline
#answer
#delete
