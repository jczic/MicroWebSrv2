
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

class UrlUtils :

    # ----------------------------------------------------------------------------

    @staticmethod
    def Quote(s, safe='/') :
        r = ''
        for c in str(s) :
            if (c >= 'a' and c <= 'z') or \
               (c >= '0' and c <= '9') or \
               (c >= 'A' and c <= 'Z') or \
               (c in '.-_') or (c in safe) :
                r += c
            else :
                for b in c.encode('UTF-8') :
                    r += '%%%02X' % b
        return r

    # ----------------------------------------------------------------------------

    @staticmethod
    def UrlEncode(s) :
        return UrlUtils.Quote(s, ';/?:@&=+$,')

    # ----------------------------------------------------------------------------

    @staticmethod
    def Unquote(s) :
        r = str(s).split('%')
        try :
            b = r[0].encode()
            for i in range(1, len(r)) :
                try :
                    b += bytes([int(r[i][:2], 16)]) + r[i][2:].encode()
                except :
                    b += b'%' + r[i].encode()
            return b.decode('UTF-8')
        except :
            return str(s)

    # ----------------------------------------------------------------------------

    @staticmethod
    def UnquotePlus(s) :
        return UrlUtils.Unquote(str(s).replace('+', ' '))

    # ============================================================================
    # ===( Class Url )============================================================
    # ============================================================================

    class Url :
    
        def __init__(self, url='') :
            self.URL = url

        # ------------------------------------------------------------------------

        def __repr__(self) :
            return self.URL if self.URL is not None else ''

        # ------------------------------------------------------------------------

        def IsHttps(self) :
            return (self._proto == 'https')

        # ------------------------------------------------------------------------

        @property
        def URL(self) :
            host = self.Host
            if host != '' :
                proto = self.Proto
                port  = self.Port
                if ( proto == 'http'  and port == 80  ) or \
                   ( proto == 'https' and port == 443 ) :
                    port = ''
                else :
                    port = ':' + str(port)
                url = proto + '://' + host + port + self.Path
                url = UrlUtils.UrlEncode(url)
                qs  = self.QueryString
                if qs != '' :
                    return url + '?' + qs
                return url
            return None

        @URL.setter
        def URL(self, value) :
            try :
                s = str(value)
                if '://' in s :
                    proto, s = s.split('://', 1)
                else :
                    proto = 'http'
            except :
                raise ValueError('URL error (%s)' % value)
            self.Proto = proto
            if '/' in s :
                host, path = s.split('/', 1)
            elif '?' in s :
                host, path = s.split('?', 1)
                path       = '?' + path
            else :
                host = s
                path = ''
            if ':' in host :
                try :
                    host, port = host.split(':')
                    self.Port  = port
                except :
                    raise ValueError('URL host:port error (%s)' % host)
            self.Host         = host
            self._queryParams = { }
            self.Path         = path

        # ------------------------------------------------------------------------

        @property
        def Proto(self) :
            return self._proto

        @Proto.setter
        def Proto(self, value) :
            value = str(value).lower()
            if value == 'http' :
                self._port = 80
            elif value == 'https' :
                self._port = 443
            else :
                raise ValueError('Unsupported URL protocol (%s)' % value)
            self._proto = value

        # ------------------------------------------------------------------------

        @property
        def Host(self) :
            return self._host
        
        @Host.setter
        def Host(self, value) :
            self._host = UrlUtils.UnquotePlus(value)

        # ------------------------------------------------------------------------

        @property
        def Port(self) :
            return self._port

        @Port.setter
        def Port(self, value) :
            try :
                p = int(value)
            except :
                raise ValueError('Port must be an integer value')
            if p <= 0 or p >= 65536 :
                raise ValueError('Port must be greater than 0 and less than 65536')
            self._port = p

        # ------------------------------------------------------------------------

        @property
        def Path(self) :
            return self._path

        @Path.setter
        def Path(self, value) :
            x = value.split('?', 1)
            if len(x[0]) > 0 :
                if x[0][0] != '/' :
                    x[0] = '/' + x[0]
                self._path = UrlUtils.UnquotePlus(x[0])
            else :
                self._path = '/'
            if len(x) == 2 :
                self.QueryString = x[1]

        # ------------------------------------------------------------------------

        @property
        def QueryString(self) :
            r = ''
            for param in self._queryParams :
                if param != '' :
                    if r != '' :
                        r += '&'
                    r += UrlUtils.Quote(param) + '=' + UrlUtils.Quote(self._queryParams[param])
            return r

        @QueryString.setter
        def QueryString(self, value) :
            self._queryParams = { }
            for x in value.split('&') :
                param = x.split('=', 1)
                if param[0] != '' :
                    value = UrlUtils.Unquote(param[1]) if len(param) > 1 else ''
                    self._queryParams[UrlUtils.Unquote(param[0])] = value

        # ------------------------------------------------------------------------

        @property
        def QueryParams(self) :
            return self._queryParams

        @QueryParams.setter
        def QueryParams(self, value) :
            if not isinstance(value, dict) :
                raise ValueError('QueryParams must be a dict')
            self._queryParams = value

    # ============================================================================
    # ============================================================================
    # ============================================================================
