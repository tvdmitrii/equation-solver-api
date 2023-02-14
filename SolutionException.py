def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def dicts_update_existing(dictTo: dict, dictFrom: dict):
    common_keys = dictTo.keys() & dictFrom.keys()

    for key in common_keys:
        dictTo[key] = dictFrom[key]


class SolutionException(Exception):
    pass
