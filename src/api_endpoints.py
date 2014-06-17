'''
Created on Jun 10, 2014

@author: anroco
'''

from flask import Blueprint
import views_users

endpoints = Blueprint('endpoints', __name__)

endpoints.add_url_rule('/login', 'login', views_users.login)
endpoints.add_url_rule('/token/getTw', 'auth_twitter',
                       views_users.auth_twitter)
endpoints.add_url_rule('/<string:nickname>', 'home', views_users.home)
endpoints.add_url_rule('/<string:nickname>/profile', 'profile',
                       views_users.profile, methods=['GET', 'POST'])
endpoints.add_url_rule('/ask/q', 'ask', views_users.create_question,
                       methods=['GET', 'POST'])
endpoints.add_url_rule('/ask/a/<string:question>', 'answer',
                       views_users.create_answer, methods=['GET', 'POST'])
endpoints.add_url_rule('/show/<string:question>', 'show',
                       views_users.view_alone)
endpoints.add_url_rule('/finder/finderdown', 'finderdown',
                       views_users.finderdown)
endpoints.add_url_rule('/', 'timeline',
                       views_users.timeline_public)
endpoints.add_url_rule('/finder/<string:find>', 'finder',
                       views_users.finder)
endpoints.add_url_rule('/ask/wa', 'update_post', views_users.update_post,
                       methods=['POST'])
endpoints.add_url_rule('/logout', 'logout', views_users.logout)
endpoints.add_url_rule('/ask/del', 'delete_post', views_users.delete_post,
                       methods=['POST'])


endpoints.add_url_rule('/about', 'about',
                       views_users.temp)
