'''
Created on Jun 10, 2014

@author: anroco
'''

from flask.ext.restful import fields
from commons import to_List

profile_user = {'nickname': fields.String,
                'name': fields.String,
                'email': fields.String,
                'registered': fields.String,
                'link_image': fields.String,
                'total_post': fields.Integer,
                'score_answers': fields.Integer,
                'skills': to_List}
