import six
from django.conf import settings
from django.http import Http404
from rest_framework.views import exception_handler


def perform_errors(errors):
    if isinstance(errors, dict):
        return [{field: perform_errors(value)} for field, value in errors.items()]

    if isinstance(errors, list):
        if all(isinstance(error, six.text_type) for error in errors):
            return ' '.join(errors)

        return [perform_errors(error) for error in errors]

    return errors


def get_firs_not_null(iterator):
    return next(val for val in iterator if val)


def get_first_error_code(codes):
    if isinstance(codes, dict):
        return get_first_error_code(list(codes.items())[0])

    if isinstance(codes, list):
        return get_first_error_code(get_firs_not_null(codes))

    if isinstance(codes, tuple) and len(codes) == 2:

        # first item is always error field name and second is message,
        # message can be nested error if it is a list
        if isinstance(codes[1], six.text_type):
            return codes

        if isinstance(codes[1], list):
            return get_first_error_code((codes[0], get_firs_not_null(codes[1])))

        return get_first_error_code(codes[1])

    return codes


STATUS = {404: 'not_found_error', 400: 'validation_error'}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        errors = perform_errors(data)
        response.data = {'errors': errors}
        try:
            error_field, error_message = get_first_error_code(data)
        except ValueError:
            error_field, error_message = settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"], get_first_error_code(data)
        if isinstance(exc, Http404):
            response.data['code'] = 'not_found'
        else:
            response.data['code'] = error_message.code

        if response.data['code'] == 'required':
            response.data['message'] = "{field} {message}".format(
                field=error_field.capitalize(),
                message=error_message.replace("This", "")
            )
        else:
            if error_field == settings.REST_FRAMEWORK["NON_FIELD_ERRORS_KEY"]:
                response.data['message'] = str(error_message)
            else:
                try:
                    label = data.serializer.fields[error_field].label
                except (AttributeError, KeyError):
                    label = error_field.replace('_', ' ')

                response.data['message'] = f'Field {label} is not filled correctly: {error_message}'
        response.data['status_code'] = response.status_code
        response.data['status'] = STATUS.get(response.status_code, 'error')
    return response
