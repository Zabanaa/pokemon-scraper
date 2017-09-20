class RequestError(Exception):

    """Docstring for RequestError. """

    def __init__(self, error_code, error_message):
        self.error_code  = error_code
        self.error_message = error_message


