import re
from aiohttp import web

from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Tuple,
    TypeVar,
    Type,
    Union)

class Or(list):
    def __init__(self, *args):
        super().__init__()
        self.extend(args)


_primitive = (str, bytes, int, float, bool)


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


class StrongParameters(dict):
    def __init__(self, *args):
        super().__init__(*args)

    async def parse(self, request, parse_body=True):
        self.__parse_multi_dict(request.query)
        if parse_body:
            self.__parse_multi_dict(await request.post())
        return self

    def with_routes(self, request):
        for k,v in request.match_info.items():
            self[k]=v
        return self

    def require(self, *args):
        data = self.permit(*args)
        for arg in args:
            if type(arg) == str:
                if arg not in data:
                    raise web.HTTPBadRequest()
            elif type(arg) == Or:
                found = False
                for item in arg:
                    if item in data:
                        found = True
                        break
                if not found:
                    raise web.HTTPBadRequest()
        return data

    def typesafe(self, args):
        ret = StrongParameters()
        for arg, required_type in args.items():
            converted = convert_type(self.get(arg), required_type)
            if not converted.valid:
                raise web.HTTPBadRequest()
            ret[arg] = converted.value

        return ret

    def permit(self, *args):
        # Examples:
        #   params = {'a': '1', 'b': '2', 'c': '3', 'd': ['4', '5'], 'e': {'f': '6', 'g': '7'} }
        #
        #   params.permit('a', 'b') => {'a': 1, 'b': 2}
        #   params.permit('a', 'b', 'd') => {'a': '1', 'b': '2'}
        #   params.permit(str) => {'a': '1', 'b': '2', c: '3'}
        #   params.permit({'e': ['f']}) => {'e': {'f': '6'}}
        #
        #
        #   params = {  'a': {'1': {'a': '1', 'b': '2', 'c': '3'}, '2': {'a': '4', 'b': '5'}} })
        #
        #   params.permit({'a': {str: ['a', 'c']}}) =>   {  'a': {'1': {'a': '1', 'c': '3'}, '2': {'a': '4'}} })
        #   params.permit({'a': {list: ['a', 'c']}}) =>  {  'a': [{'a': '1', 'c': '3'}, {'a': '4'}] })
        #
        ret = StrongParameters()
        for arg in args:
            if type(arg) is list:
                ret = StrongParameters({**ret, **self.permit(*arg)})

            elif type(arg) is Or:
                for item in arg:
                    v = self.get(item)
                    if type(v) is str:
                        ret[item] = v

            elif type(arg) is str:
                v = self.get(arg)
                if type(v) is str:
                    ret[arg] = v

            elif type(arg) == dict:
                for k, v in arg.items():
                    params = self.get(k)
                    if params:
                        child_params = params.permit(v)
                        if child_params:
                            ret[k] = child_params

                    elif k == str:
                        for sk, params in self.items():
                            child_params = StrongParameters.__subpermit(params, v)
                            if child_params:
                                ret[sk] = child_params

                    elif k == list:
                        lst = []
                        for sk in sorted(self.keys()):
                            params = self[sk]
                            child_params = StrongParameters.__subpermit(params, v)
                            if child_params:
                                lst.append(child_params)
                        return lst

            elif type(arg) == type:
                for k, v in self.items():
                    if type(v) == arg:
                        ret[k] = v
        return ret

    @staticmethod
    def __subpermit(params, v):
        if type(v) is list:
            if type(params) is StrongParameters:
                return params.permit(v)

    def __parse_multi_dict(self, q):
        for k, val in q.items():
            if '[' in k:
                keys = re.findall(r'\[(\w*)\]', k)
                kp = k.split('[')[0]
                vp = self
                for kk in keys:
                    v = None
                    if kk == '':
                        v = []
                        if type(vp) is StrongParameters:
                            if type(vp.get(kp)) is list:
                                v = vp[kp]
                            else:
                                vp[kp] = v
                        else:
                            vp.append(v)
                    else:
                        v = StrongParameters()
                        if type(vp) is StrongParameters:
                            if type(vp.get(kp)) is list:
                                v = vp[kp]
                            elif type(vp.get(kp)) is StrongParameters:
                                v = vp[kp]
                            else:
                                vp[kp] = v
                        else:
                            vp.append(v)
                    vp = v
                    kp = kk
                if type(vp) is list:
                    vp.append(val)
                else:
                    vp[kp] = val
            else:
                self[k] = val
        return self
