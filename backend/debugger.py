def raise_locals(f):
    import sys, traceback
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            ext = traceback.StackSummary.extract(traceback.walk_tb(exc_traceback), capture_locals=True)
            locals_ = ext[-1].locals
            if locals_:
                print('{' + ', '.join([f"'{k}': {v}" for k, v in locals_.items()]) + '}')
            raise
    return wrapper