'''
Created on Jun 6, 2014

@author: anroco
'''

import os
from flask import Flask
from api_endpoints import endpoints
from api_errors import errors

SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY_ANONYMOUS = os.environ.get('SECRET_KEY_ANONYMOUS')
OX_TOKEN_USER_LIFETIME = int(os.environ.get('OX_TOKEN_USER_LIFETIME'))
OX_TOKEN_GUEST_USER_LIFETIME = int(os.environ.get('OX_TOKEN_GUEST_USER_LIFETIME'))
DEBUG = os.environ.get('FLASK_DEBUG') in ['True', 'true']

application = Flask(__name__)
application.config.from_object(__name__)

#registrar los blueprints en la aplicacion
application.register_blueprint(endpoints)
application.register_blueprint(errors)

if __name__ == "__main__":
    application.run(host='0.0.0.0')
