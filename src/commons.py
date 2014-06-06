'''
Created on Jun 6, 2014

@author: anroco
'''


def get_token_twitter():

    from flask import current_app, request, url_for
    from flask_oauth import OAuth

    config = current_app.config

    tw_auth = OAuth().remote_app(name=config['TW_NAME'],
                            base_url=config['TW_BASE_URL'],
                            request_token_url=config['TW_REQUEST_TOKEN_URL'],
                            access_token_url=config['TW_ACCESS_TOKEN_URL'],
                            authorize_url=config['TW_AUTHORIZE_URL'],
                            consumer_key=config['TW_CONSUMER_KEY'],
                            consumer_secret=config['TW_CONSUMER_SECRET'])

    tw_auth.authorize(callback=url_for('register_user',
        next=request.args.get('home') or request.referrer or None))
