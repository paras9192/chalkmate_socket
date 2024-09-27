from ariadne import format_error
from django.conf import settings
ERROR_MESSAGE = getattr(settings, 'CUSTOM_ERROR_MESSAGE') #
LOGGEER = settings.LOGGEER

def custom_error_format(error, debug=False):
    if debug:
        return format_error(error, debug)
    formatted = error.formatted
    if error.original_error:
        formatted['formatted_message'] = error.message
    else:
        formatted['formatted_message'] = ERROR_MESSAGE
    formatted["status"] = 0
    formatted["message"] = error.message
    LOGGEER.debug(formatted)
    return formatted