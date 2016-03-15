def passes(return_value=None):
    """
    Simple test function to wrap that always passes.
    """
    return return_value or 1


def fails(exception=None):
    """
    Simple test function to wrap that always raises the given exception or just
    the Exception class.
    """
    exception = exception or Exception()
    raise exception
