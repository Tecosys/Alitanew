import asyncio
from collections import OrderedDict
from functools import _make_key, wraps

def async_cache(maxsize=128, event_loop=None):
    cache = OrderedDict()
    if event_loop is None:
        event_loop = asyncio.get_event_loop()
    awaiting = dict()

    async def run_and_cache(func, args, kwargs):
        """await func with the specified arguments and store the result
        in cache."""
        result = await func(*args, **kwargs)
        key = _make_key(args, kwargs, False)
        cache[key] = result
        if maxsize:
            if len(cache) > maxsize:
                cache.popitem(False)
        cache.move_to_end(key)
        return result

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = _make_key(args, kwargs, False)
            if key in cache:
                return cache[key]
            if key in awaiting:
                task = awaiting[key]
                return await asyncio.wait_for(task, timeout=None, loop=event_loop)
            task = asyncio.ensure_future(run_and_cache(func, args, kwargs), loop=event_loop)
            awaiting[key] = task
            result = await asyncio.wait_for(task, timeout=None, loop=event_loop)
            del awaiting[key]
            return result
        return wrapper
    return decorator
