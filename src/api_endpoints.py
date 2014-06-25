'''
Created on Jun 10, 2014

@author: anroco
'''

from flask import Blueprint
import views

endpoints = Blueprint('endpoints', __name__)

endpoints.add_url_rule('/login', 'login', views.login)
endpoints.add_url_rule('/token/getTw', 'auth_twitter',
                       views.auth_twitter)
endpoints.add_url_rule('/<string:nickname>', 'home', views.home)
endpoints.add_url_rule('/<string:nickname>/profile', 'profile',
                       views.profile, methods=['GET', 'POST'])
endpoints.add_url_rule('/ask/q', 'ask', views.create_question,
                       methods=['GET', 'POST'])
endpoints.add_url_rule('/ask/a', 'answer', views.create_answer,
                       methods=['POST'])
endpoints.add_url_rule('/show/<string:question>', 'show',
                       views.view_alone)
endpoints.add_url_rule('/finder/finderdown', 'finderdown',
                       views.finderdown)
endpoints.add_url_rule('/', 'timeline',
                       views.timeline_public)
endpoints.add_url_rule('/finder/<string:find>', 'finder',
                       views.finder)
endpoints.add_url_rule('/ask/wa', 'update_post', views.update_post,
                       methods=['POST'])
endpoints.add_url_rule('/logout', 'logout', views.logout)
endpoints.add_url_rule('/ask/del', 'delete_post', views.delete_post,
                       methods=['GET', 'POST'])


endpoints.add_url_rule('/about', 'about',
                       views.temp)
