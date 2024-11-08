from collections.abc import Callable

from GameEngines import AbsBoardState


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

def ignore_cache(func):
    """
    Wrapper for the `copy` method of BoardState to let the copy method ignore the moves cache.
    :param func: `copy` function.
    :return: set of moves allowed for this state
    """
    def wrapper(self, *args, **kwargs):
        # removes the cache before the copy
        if hasattr(self, '__move_cache'):
            delattr(self, '__move_cache')

        return func(self, *args, **kwargs)
    return wrapper

def get_cache(func):
    """
    Wrapper for the `_get_data` function that adds the move cache to the data dict if there was one.
    :param func: the `_get_data` function of default SaveModules.
    """
    def wrapper(state: AbsBoardState, *args, **kwargs):
        data = func(state, *args, **kwargs)

        if hasattr(state, '__move_cache'):
            data["__move_cache"] = list(state.__move_cache)

        return data
    return wrapper


def put_cache(to_move: Callable):
    """
    Wrapper for the `_put_data` function that adds the move cache to the BoardState if there was one.
    :param to_move: the function to change Json moves back to Move type
    """
    def wrapper_1(func):

        def wrapper(data: dict, *args, **kwargs):
            obj = func(data, *args, **kwargs)

            if "__move_cache" in data:
                obj.__move_cache = set(to_move(m) for m in data["__move_cache"])

            return obj
        return wrapper
    return wrapper_1