

# get value from dict by chained keys like a.b.c
def safe_get(d, keys, default=None):
    if not isinstance(keys, list):
        keys = [keys]
    if d is None:
        return default
    for key in keys:
        d = d.get(key)
        if d is None:
            return default
    return d