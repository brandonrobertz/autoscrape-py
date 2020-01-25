# -*- coding: UTF-8 -*-


def pop_debugger():
    """
    Drop into an ipython debugger at any point in the code. Sometimes
    there are weird scope issues (can't use local variables from the
    state of the code inside things like lambdas, comprehensions, etc.)
    This is here so we can mitigate these issues in a single place if the
    need arises.
    """
    import IPython
    IPython.embed()
    import time
    time.sleep(2)
