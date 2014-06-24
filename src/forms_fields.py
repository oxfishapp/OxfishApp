'''
Created on Jun 19, 2014

@author: anroco
'''

import re
from wtforms import (Form, StringField, HiddenField, FieldList, TextAreaField,
                     validators as v)
from validators import *

rm_spaces_repeated = lambda x: re.sub(' +', ' ', x.strip() if x else '')
rm_newline_repeated = lambda x: re.sub(r'(\r\n|\n|\r)+', '\n', x if x else '')
invert_value = lambda x: -1 if int(x) not in [0, 1] else 0 if int(x) else 1
to_int_value = lambda x: int(x)


class FieldListSkills(FieldList):

    @property
    def data(self):
        return [f.data for f in self.entries if f.data]

    @property
    def errors_list(self):
        return [e for e in self.errors if not isinstance(e, list)]


class RegisterUserForm(Form):

    email = StringField(validators=[v.required(),
                                    v.regexp(EMAIL_REGEX,
                                             message=EMAIL_MESSAGE)],
                        filters=[rm_spaces_repeated])

    skills = FieldListSkills(StringField(validators=[
                                        v.required(),
                                        v.Length(max=15,
                                           message=LENGTH_MESSAGE.format(15)),
                                        v.regexp(FORMAT_SKILLS_REGEX,
                                           message=FORMAT_SKILLS_MESSAGE)],
                                   filters=[rm_spaces_repeated]),
                       validators=[ItemsRepeated()])


class CreatePostFields(Form):

    message140 = TextAreaField(validators=[
                                     v.required(),
                                     v.Length(max=140,
                                        message=LENGTH_MESSAGE.format(140))],
                             filters=[rm_spaces_repeated, rm_newline_repeated])

    link = StringField(validators=[v.url(), v.optional()])

    geolocation = HiddenField(id='latLong',
                              validators=[v.optional(),
                                          v.regexp(LATLONG_REGEX,
                                                    message=LATLONG_MESSAGE)])


class CreateQuestionForm(CreatePostFields):

    skills = FieldListSkills(StringField(validators=[
                                        v.Length(max=15,
                                           message=LENGTH_MESSAGE.format(15)),
                                        v.regexp(FORMAT_SKILLS_REGEX,
                                           message=FORMAT_SKILLS_MESSAGE)],
                                   filters=[rm_spaces_repeated]),
                             validators=[ItemsRepeated(), LengthListItems(1)])


class CreateAnswerForm(CreatePostFields):

    key_post_original = HiddenField(validators=[v.Required(), v.UUID()])


class UpdatePostForm(Form):

    question = HiddenField(validators=[v.Required(), v.UUID()])
    answer = HiddenField(validators=[v.Required(), v.UUID()])
    key_user = HiddenField(validators=[v.Required(), v.UUID()])
    state = HiddenField(validators=[v.NumberRange(min=0, max=1)],
                        filters=[invert_value])


class DeletePostForm(Form):

    hash_key = HiddenField(validators=[v.Required(), v.UUID()])
    is_question = HiddenField(validators=[v.NumberRange(min=0, max=1)],
                              filters=[to_int_value])
