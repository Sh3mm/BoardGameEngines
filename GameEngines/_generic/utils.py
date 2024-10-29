def cache_moves(func):
    """
    Wrapper for the `get_legal_moves` method of BoardState to allow for generic moves caching in case of multiple lookups.
    :param func: `get_legal_moves` function.
    :return: set of moves allowed for this state
    """
    def wrapper(self, *args, cache=False, **kwargs):
        if not cache and not hasattr(self, '__move_cache'):
            return func(self, *args, **kwargs)

        if hasattr(self, '__move_cache'):
            return self.__move_cache

        self.__move_cache = func(self, *args, **kwargs)
        return self.__move_cache
    return wrapper
