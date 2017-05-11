import re


class StrongParameters(dict):
    def __init__(self, *args):
        super().__init__(*args)

    async def parse(self, request):
        self.__parse_multi_dict(request.query)
        self.__parse_multi_dict(await request.post())
        return self

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
