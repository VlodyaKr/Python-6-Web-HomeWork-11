from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load, validates_schema, post_load
from marshmallow.fields import Email, Date


class AllowEmptyAnyField(object):
    def _validate(self, value):
        if value == '':
            return ''
        return super(AllowEmptyAnyField, self)._validate(value)

    def _deserialize(self, value, *args, **kwargs):
        if value == '':
            return ''
        return super(AllowEmptyAnyField, self)._deserialize(value, *args, **kwargs)


class AllowEmptyEmailField(AllowEmptyAnyField, fields.Email):
    pass


class AllowEmptyDateField(AllowEmptyAnyField, fields.Date):
    pass


class RegistrationSchema(Schema):
    nick = fields.Str(validate=validate.Length(min=3), required=True)
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=6), required=True)


class LoginSchema(Schema):
    remember = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=6), required=True)


class NoteDateSchema(Schema):
    date = fields.Date(required=True)
    days = fields.Integer()


class ContactSchema(Schema):
    contact_name = fields.Str(validate=validate.Length(min=3), required=True)
    phone = fields.Method(deserialize='_phone_check')
    email = AllowEmptyEmailField()
    address = fields.Str()
    birthday = AllowEmptyDateField()

    def _phone_check(self, value):
        def is_code_valid(phone_code: str) -> bool:
            if phone_code[:2] in ('03', '04', '05', '06', '09') and phone_code[2] != '0' and phone_code != '039' or \
                    phone_code == '050':
                return True
            return False

        result = None
        print(value)
        phone_ = value.removeprefix('+').replace('(', '').replace(')', '').replace('-', '')
        if value == '':
            return ''
        if phone_.isdigit():
            if phone_.startswith('0') and len(phone_) == 10 and is_code_valid(phone_[:3]):
                result = '+38' + phone_
            if phone_.startswith('380') and len(phone_) == 12 and is_code_valid(phone_[2:5]):
                result = '+' + phone_
            if 10 <= len(phone_) <= 14 and not phone_.startswith('0') and not phone_.startswith('380'):
                result = '+' + phone_
        if result is None:
            raise ValidationError('Phone number is not valid.')
        return result


class EmailCheck(Schema):
    email = fields.Email()
