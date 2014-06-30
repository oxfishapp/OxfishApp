# -*- coding: utf-8 -*-
'''
Created on Jun 6, 2014

@author: anroco
'''

from flask import Blueprint, render_template

errors = Blueprint('ox_errors', __name__)


@errors.app_errorhandler(404)
def error_code_404(e):
    return render_template('_errors.html', code=404,
                           message='Oops!, that resource doesn’t exist.').encode('utf-8')


@errors.app_errorhandler(401)
def error_code_401(e):
    return render_template('_errors.html', code=401,
                           message='Oops!, Authentication Required.')


@errors.app_errorhandler(400)
def error_code_400(e):
    return render_template('_errors.html', code=400,
                           message='Oops!, Bad Request.')


@errors.app_errorhandler(500)
def error_code_500(e):
    return render_template('_errors.html', code=500,
                           message='Oops!, Internal Server Error.')
