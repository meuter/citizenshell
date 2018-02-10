from uritools import urisplit


class ParsedUri:

    def __init__(self, uri, **kwargs):
        parsed_uri = urisplit(uri)
        self.scheme = parsed_uri.scheme
        self.parse_userinfo(parsed_uri, kwargs)
        self.parse_hostinfo(parsed_uri, kwargs)
        self.validate()

    def parse_hostinfo(self, parsed_uri, kwargs):
        hostname_from_uri = parsed_uri.gethost(default=None)
        if not hostname_from_uri or str(hostname_from_uri) == '':
            self.hostname = None
        else:
            self.hostname = str(hostname_from_uri)
        self.port = self.get_uri_part("port", parsed_uri.getport(default=None), kwargs)

    def parse_userinfo(self, parsed_uri, kwargs):
        username_from_uri = None
        password_from_uri = None
        userinfo = parsed_uri.getuserinfo()
        if userinfo:
            if userinfo.find(":") != -1:
                username_from_uri, password_from_uri = userinfo.split(":")
                if username_from_uri == "":
                    username_from_uri = None                    
            else:
                username_from_uri = userinfo
        self.username = self.get_uri_part("username", username_from_uri, kwargs)
        self.password = self.get_uri_part("password", password_from_uri, kwargs)

    def validate(self):
        if self.scheme in ["telnet", "ssh"]:
            if not self.hostname or not self.username:
                raise RuntimeError("scheme '%s' requires 'hostname' and 'username'", self.scheme)

    @staticmethod
    def get_uri_part(argname, from_uri, kwargs):
        from_kwargs = kwargs.get(argname, None)
        if from_kwargs and from_uri:
            raise RuntimeError("'%s' provided both in uri and as argument")
        elif from_uri and not from_kwargs:
            return from_uri
        return from_kwargs
