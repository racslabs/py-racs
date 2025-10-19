class RacsException(Exception):
    """
    Exception raised for error responses returned by the RACS server.

    The server may return an error message indicating that a command failed
    or an internal error occurred. This exception encapsulates that error response.
    """

    def __init__(self, message):
        """
        Initialize a RACS exception.

        Parameters
        ----------
        message : str
            The error message returned by the RACS server.
        """
        super().__init__(message)
