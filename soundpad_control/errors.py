class SoundpadError(Exception):
    """Base class for exceptions related to Soundpad."""

class SoundpadRequestError(SoundpadError):
    """Exception raised for errors that occur during a Soundpad request.

    Attributes:
        message -- explanation of the error
        response -- response object containing details of the error
    """
    
    def __init__(self, response=None, message = "An error occurred while making a request to Soundpad."):
        super().__init__(message)
        self.response = response

    def __str__(self):
        error_message = f"{self.args[0]}"
        if self.response is not None:
            error_message += f" (Response: {self.response})"
        return error_message

class SoundpadNotLaunchedError(SoundpadError):
    """Raised when Soundpad is not launched."""
    def __init__(self, message="Soundpad is not launched or the pipe does not exist."):
        self.message = message
        super().__init__(self.message)