from uritools import urisplit


class ParsedUri:

    def __init__(self, uri=None, **kwargs):
        parsed_uri = urisplit(uri or "local://")
        self.scheme = parsed_uri.scheme
        self.kwargs = dict(kwargs)
        self.baudrate = None
        self.parse_userinfo(parsed_uri)
        self.parse_deviceinfo(parsed_uri)
        self.parse_hostinfo(parsed_uri)
        self.validate()
        self.fill_defaults()

    def parse_hostinfo(self, parsed_uri):
        if self.scheme == "serial":            
            path_from_uri = parsed_uri.getpath()
            hostname_from_uri = parsed_uri.gethost(default=None).upper()
            port_from_uri = path_from_uri if path_from_uri else hostname_from_uri
            self.port = self.get_uri_part("port", port_from_uri)
            baudrate_from_uri = parsed_uri.getquerydict().get("baudrate", [None])[0]
            self.baudrate = int(self.get_uri_part("baudrate", baudrate_from_uri))            
        else:
            hostname_from_uri = parsed_uri.gethost(default=None)
            if not hostname_from_uri or str(hostname_from_uri) == '':
                self.hostname = None
            else:
                self.hostname = str(hostname_from_uri)
            self.port = self.get_uri_part("port", parsed_uri.getport(default=None))

    def parse_userinfo(self, parsed_uri):
        username_from_uri = None
        password_from_uri = None
        userinfo = parsed_uri.getuserinfo()
        if userinfo:
            index = userinfo.find(":")
            if index != -1:                
                username_from_uri, password_from_uri = userinfo[:index], userinfo[index+1:]
                if username_from_uri == "":
                    username_from_uri = None                    
            else:
                username_from_uri = userinfo
        self.username = self.get_uri_part("username", username_from_uri)
        self.password = self.get_uri_part("password", password_from_uri)

    def parse_deviceinfo(self, parsed_uri):
        self.device = parsed_uri.gethost()

    def validate(self):
        if self.scheme in ("telnet", "ssh"):
            if not self.hostname or not self.username:
                raise RuntimeError("scheme '%s' requires 'hostname' and 'username'", self.scheme)
        if self.scheme in ("adb", "adb+tcp"):
            if not self.hostname:
                raise RuntimeError("scheme '%s' requires 'hostname'", self.scheme)
        if self.scheme in ("adb+usb",):
            if not self.device:
                raise RuntimeError("scheme '%s' requires 'device'", self.scheme)

    def fill_defaults(self):
        if self.scheme == "telnet":
            self.port = self.port or 23
        elif self.scheme == "ssh":
            self.port = self.port or 22
        elif self.scheme in ("adb","adb+tcp"):
            self.port = self.port or 5555
        elif self.scheme == "adb+usb":
            self.port = None

        if self.scheme in ("telnet", "adb", "ssh"):
            self.device = None
        elif self.scheme == "adb+usb":
            self.hostname = None
            self.scheme = "adb"
        elif self.scheme == "adb+tcp":
            self.device = None
            self.scheme = "adb"
            

    def get_uri_part(self, argname, from_uri):
        from_kwargs = self.kwargs.get(argname, None)
        
        if argname in self.kwargs:
            del self.kwargs[argname]

        if from_kwargs and from_uri:
            raise RuntimeError("'%s' provided both in uri and as argument")
        elif from_uri and not from_kwargs:
            return from_uri
        return from_kwargs

    
