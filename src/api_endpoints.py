# -*- coding: utf-8 -*-
#!/usr/bin/env python
#!flask/bin/python

'''
Created on May 8, 2014

@author: anroco
'''

from flask import Blueprint
import views_users

endpoints = Blueprint('endpoints', __name__)

endpoints.add_url_rule('/login', 'login', views_users.login)
endpoints.add_url_rule('/getTokenTw', 'auth_twitter', views_users.auth_twitter)
endpoints.add_url_rule('/register', 'register',
                       views_users.register_email_skills)
# endpoints.add_url_rule('/<string:nickname>/profile', 'user_profile',
#                       views_users.profile)
endpoints.add_url_rule('/home', 'home', views_users.home)
endpoints.add_url_rule('/home/profile', 'profile', views_users.profile)
