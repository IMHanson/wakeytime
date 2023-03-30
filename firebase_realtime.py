import ujson
import urequests as requests

_URL = ""

class Auth(object):
        
    def _get_auth_url(self, name):
        _auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:"
        urls = {
            "sign_in" : f"{_auth_url}signInWithPassword",
            "sign_up" : f"{_auth_url}accounts:signUp",
            "sign_out" : f"{_auth_url}accounts:signUp",
            "verify": f"{_auth_url}verifyPassword"
            }
        return urls[name]  + "?key={api_key}"

    def add_user(self, user_email, password, api_key):
        #print("Adding user")
        _url = self._get_auth_url("sign_up").format(api_key=api_key)
        data = {"email": user_email,
                "password": password,
                "returnSecureToken": True}
        post_data = ujson.dumps(data)
        #print(f"url: {_url}")
        #print(f"PostData: {post_data}")
        res = None
        try:
            res = requests.post(_url,
                                headers={'content-type': 'application/json'},
                                data=data)
        except Exception as e:
            print(f"error: {e}")
            if res:
                print(f"Res: {res}")
            return e, None
        header_data = ''
        #print(dir(res))
        if res.status_code == 200 :
            res_data = res.json()
            #print(res_data)
            header_data = { "content-type": 'application/json; charset=utf-8'}
            for header in ("idToken", "email", "refreshToken", "expiresIn", "localId"):
                header_data[header] = str(res_data[header])
        else:
            return False, res.json()
        return True, header_data

    def validate_user(self, user_email, password, api_key):
        _url = self._get_auth_url("sign_in").format(api_key=api_key)
        #print(f"url: {_url}")
        data = {"email":user_email,"password":password,"returnSecureToken":True}
        post_data = ujson.dumps(data)
        #print(post_data)
        try:
            res = requests.post(_url,
                                headers = {'content-type': 'application/json'},
                                data=post_data)
        except Exception as e:
            print(f"Error: {e}")
            return False, e
        header_data = ''
        #print(dir(res))
        #print(res.text)
        if res.status_code == 200 :
            res_data = res.json()
            #print(res_data)
            header_data = { "content-type": 'application/json; charset=utf-8'}
            for header in ("idToken", "email", "refreshToken", "expiresIn", "localId"):
                header_data[header] = str(res_data[header])
        else:
            return False, res.json()
        return True, header_data

class Realtime(object):
    def __init__(self, url, header):
        self.BASE_URL = url
        self.header = header
        self.header['content-type'] = 'application/json'
        self.id_token = self.header['idToken']

    def __action(self, action_name, rel_url, **kargs):
        _url = f"{self.BASE_URL}/{rel_url}/.json?auth={self.id_token}"
        post_data = ujson.dumps(kargs.get('data', {}))
        #print(_url)
        func = getattr(requests, action_name)
        res = func(_url, headers=self.header, data=post_data)
        res_data = res.json()
        if res.status_code == 200 :
            flg = True
        else:
            return False, res.json()
        return True, res_data

    def put(self, rel_url, data):

        flg, ret_data = self.__action("put", rel_url, data=data) 
        return flg, ret_data

    def patch(self, rel_url, data_tag):
        flg, ret_data = self.__action("patch", rel_url, data=data_tag) 
        return flg, ret_data

    def post(self, rel_url, data_tag):
        flg, ret_data = self.__action("post", rel_url, data=data_tag) 
        return flg, ret_data

    def get(self, rel_url, limit=-1):
        flg, ret_data = self.__action("get", rel_url) 
        return flg, ret_data


    def delete(self, rel_url):
        flg, ret_data = self.__action("delete", rel_url) 
        return flg, ret_data

