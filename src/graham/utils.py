def _strip_leading_underscore(s):
    return s if s[0] != '_' else s[1:]


def _dict_strip(d, keys):
    return {
        _strip_leading_underscore(k): v
        for k, v in d.items()
        # if k not in keys
    }
