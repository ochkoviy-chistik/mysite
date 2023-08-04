class NotAuthorizeException (Exception):
    def __init__(self):
        self.message = 'Error'
        super().__init__(self.message)
