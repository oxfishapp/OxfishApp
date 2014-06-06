'''
Created on Jun 6, 2014

@author: anroco
'''

from flask import Flask


OX_SECRET_KEY = "kEv7FEBT8rarwB41Hf72Bw50HbY6dyOU4CiwXHkFdExs5NgVQWaray6civgs4aYX"
SECRET_KEY_ANONYMOUS = 'YGWF5VLNhwduPtfMisczxgYDWRqoG5bW'
DB_HOST = 'localhost'
DB_PORT = 8000
DB_AWS_ACCESS_KEY_ID = 'DEVDB'
DB_AWS_SECRET_KEY = 'DEVDB'
DB_IS_SECURE = False
DB_TABLE_PREFIX = ''
DB_LIMIT = 10
TW_CONSUMER_KEY = 'QbINcoPerlOi4Y4QD3wSjHJKp'
TW_CONSUMER_SECRET = 'ZBR4eNAo6KUK0gnZO2vm2JKLZdU4gh3DVbcnSibC42diBz1fiJ'
TW_NAME = 'restanroco'
TW_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
TW_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'
TW_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
TW_BASE_URL = 'https://api.twitter.com/1.1/'


application = Flask(__name__)
application.config.from_object(__name__)



if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=False)
