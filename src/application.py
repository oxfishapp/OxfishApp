'''
Created on Jun 6, 2014

@author: anroco
'''

import os
from flask import Flask
from api_endpoints import endpoints
from api_errors import errors

#SECRET_KEY = '7m3Cx7dgNdrk6U9mtRjbbJm92czTxk83xqbwWZjAya8GWqPbwV948kzd4WDfgsxy'
#SECRET_KEY_ANONYMOUS = 'YGWF5VLNhwduPtfMisczxgYDWRqoG5bW'
#OX_TOKEN_USER_LIFETIME = 3600
#OX_TOKEN_GUEST_USER_LIFETIME = 900

SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY_ANONYMOUS = os.environ.get('SECRET_KEY_ANONYMOUS')
OX_TOKEN_USER_LIFETIME = int(os.environ.get('OX_TOKEN_USER_LIFETIME'))
OX_TOKEN_GUEST_USER_LIFETIME = int(os.environ.get('OX_TOKEN_GUEST_USER_LIFETIME'))

application = Flask(__name__)
application.config.from_object(__name__)

#registrar los blueprints en la aplicacion
application.register_blueprint(endpoints)
application.register_blueprint(errors)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)#, debug=True)
