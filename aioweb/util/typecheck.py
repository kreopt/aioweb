from typing import Any, Union, Tuple, Dict, List

_primitive = (str, bytes, int, float)


class TypeCheckResult(object):
    def __init__(self, valid=False, cleaned=None):
        self.valid = valid
        self.value = cleaned


def convert_type(obj: Any,
                 candidate_type: Any) -> TypeCheckResult:
    if candidate_type in _primitive:
        try:
            return TypeCheckResult(True, candidate_type(obj))
        except:
            return TypeCheckResult()

    if candidate_type == bool:
        try:
            intval = int(obj)
        except (ValueError, TypeError):
            intval = 0
        return TypeCheckResult(True, (obj in ('t', 'true')) or (intval > 0))

    # Any accepts everything
    if type(candidate_type) == type(Any):
        return TypeCheckResult(True, obj)

    # Union, at least one match in __args__
    if type(candidate_type) == type(Union):
        for t in candidate_type.__args__:
            if t is type(None):
                r = TypeCheckResult(not obj, None)
            else:
                r = convert_type(obj, t)
            if r.valid:
                return r
        return TypeCheckResult()

    # Tuple, each element matches the corresponding type in __args__
    if type(candidate_type) == type(Tuple) and tuple in candidate_type.__bases__:
        if not hasattr(obj, '__len__'):
            return TypeCheckResult()
        if len(candidate_type.__args__) != len(obj):
            return TypeCheckResult()
        cleaned_tuple = []
        for (o, t) in zip(obj, candidate_type.__args__):
            r = convert_type(o, t)
            if not r.valid:
                return TypeCheckResult()
            cleaned_tuple.append(r.value)
        return TypeCheckResult(True, tuple(cleaned_tuple))

    # Dict, each (key, value) matches the type in __args__
    if type(candidate_type) == type(Dict) and dict in candidate_type.__bases__:
        if type(obj) != dict:
            return TypeCheckResult()
        cleaned_dict = {}
        for (k, v) in obj.items():
            kr = convert_type(k, candidate_type.__args__[0])
            vr = convert_type(v, candidate_type.__args__[1])
            if not (kr.valid and vr.valid):
                return TypeCheckResult()
            cleaned_dict[kr.value] = vr.value
        return TypeCheckResult(True, tuple(cleaned_dict))

    # List or Set, each element matches the type in __args__
    if type(candidate_type) == type(List) and \
            (list in candidate_type.__bases__ or set in candidate_type.__bases__):
        if not hasattr(obj, '__len__'):
            return TypeCheckResult()
        cleaned_list = []
        for o in obj:
            r = convert_type(o, candidate_type.__args__[0])
            if not r.valid:
                return TypeCheckResult()
            cleaned_list.append(r.value)
        return TypeCheckResult(True, cleaned_list if not set in candidate_type.__bases__ else set(cleaned_list))
    return TypeCheckResult()