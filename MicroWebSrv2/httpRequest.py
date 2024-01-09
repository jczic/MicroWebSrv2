
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

from   .              import *
from   .httpResponse  import HttpResponse
from   binascii       import a2b_base64
import json

# ============================================================================
# ===( HttpRequest )==========================================================
# ============================================================================

class HttpRequest :

    MAX_RECV_HEADER_LINES = 100

    # ------------------------------------------------------------------------

    def __init__(self, microWebSrv2, xasCli) :
        self._mws2   = microWebSrv2
        self._xasCli = xasCli
        self._waitForRecvRequest()

    # ------------------------------------------------------------------------

    def _recvLine(self, onRecv) :
        self._xasCli.AsyncRecvLine(onLineRecv=onRecv, timeoutSec=self._mws2._timeoutSec)

    # ------------------------------------------------------------------------

    def _waitForRecvRequest(self) :
        self._httpVer  = ''
        self._method   = ''
        self._path     = ''
        self._headers  = { }
        self._content  = None
        self._response = HttpResponse(self._mws2, self)
        self._recvLine(self._onFirstLineRecv)

    # ------------------------------------------------------------------------

    def _onFirstLineRecv(self, xasCli, line, arg) :
        try :
            elements = line.strip().split()
            if len(elements) == 3 :
                self._httpVer     = elements[2].upper()
                self._method      = elements[0].upper()
                elements          = elements[1].split('?', 1)
                self._path        = UrlUtils.UnquotePlus(elements[0])
                self._queryString = (elements[1] if len(elements) > 1 else '')
                self._queryParams = { }
                if self._queryString :
                    elements = self._queryString.split('&')
                    for s in elements :
                        p = s.split('=', 1)
                        if len(p) > 0 :
                            v = (UrlUtils.Unquote(p[1]) if len(p) > 1 else '')
                            self._queryParams[UrlUtils.Unquote(p[0])] = v
                self._recvLine(self._onHeaderLineRecv)
            else :
                self._response.ReturnBadRequest()
        except :
            self._response.ReturnBadRequest()

    # ------------------------------------------------------------------------

    def _onHeaderLineRecv(self, xasCli, line, arg) :
        try :
            elements = line.strip().split(':', 1)
            if len(elements) == 2 :
                if len(self._headers) < HttpRequest.MAX_RECV_HEADER_LINES :
                    self._headers[elements[0].strip().lower()] = elements[1].strip()
                    self._recvLine(self._onHeaderLineRecv)
                else :
                    self._response.ReturnEntityTooLarge()
            elif len(elements) == 1 and len(elements[0]) == 0 :
                self._processRequest()
            else :
                self._response.ReturnBadRequest()
        except :
            self._response.ReturnBadRequest()

    # ------------------------------------------------------------------------

    def _processRequest(self) :
        if not self._processRequestModules() :
            if not self.IsUpgrade :
                if not self._processRequestRoutes() :
                    if self._method in ('GET', 'HEAD') :
                        filename = self._mws2.ResolvePhysicalPath(self._path)
                        if filename :
                            ct = self._mws2.GetMimeTypeFromFilename(filename)
                            if ct :
                                self._response.AllowCaching = True
                                self._response.ContentType  = ct
                                self._response.ReturnFile(filename)
                            else :
                                self._response.ReturnForbidden()
                        else :
                            self._response.ReturnNotFound()
                    elif self._method == 'OPTIONS' :
                        if self._mws2.CORSAllowAll :
                            self._response.SetHeader( 'Access-Control-Allow-Methods',     '*'     )
                            self._response.SetHeader( 'Access-Control-Allow-Headers',     '*'     )
                            self._response.SetHeader( 'Access-Control-Allow-Credentials', 'true'  )
                            self._response.SetHeader( 'Access-Control-Max-Age',           '86400' )
                        self._response.ReturnOk()
                    else :
                        self._response.ReturnMethodNotAllowed()
            else :
                self._response.ReturnNotImplemented()

    # ------------------------------------------------------------------------

    def _processRequestModules(self) :
        for modName, modInstance in self._mws2._modules.items() :
            try :
                modInstance.OnRequest(self._mws2, self)
                if self._response.HeadersSent :
                    return True
            except Exception as ex :
                self._mws2.Log( 'Exception in request handler of module "%s" (%s).'
                                % (modName, ex),
                                self._mws2.ERROR )
        return False

    # ------------------------------------------------------------------------

    def _processRequestRoutes(self) :
        self._routeResult = ResolveRoute(self._method, self._path)
        if self._routeResult :
            cntLen = self.ContentLength
            if not cntLen :
                self._routeRequest()
            elif self._method != 'GET' and self._method != 'HEAD' :
                if cntLen <= self._mws2._maxContentLen :
                    def onContentRecv(xasCli, content, arg) :
                        self._content = content
                        self._routeRequest()
                        self._content = None
                    try :
                        self._xasCli.AsyncRecvData( size       = cntLen,
                                                    onDataRecv = onContentRecv,
                                                    timeoutSec = self._mws2._timeoutSec )
                    except :
                        self._mws2.Log( 'Not enough memory to read a content of %s bytes.' % cntLen,
                                        self._mws2.ERROR )
                        self._response.ReturnServiceUnavailable()
                else :
                    self._response.ReturnEntityTooLarge()
            else :
                self._response.ReturnBadRequest()
            return True
        return False

    # ------------------------------------------------------------------------

    def _routeRequest(self) :
        try :
            currentResp = self._response
            if self._routeResult.Args :
                self._routeResult.Handler(self._mws2, self, self._routeResult.Args)
            else :
                self._routeResult.Handler(self._mws2, self)
            if not currentResp.HeadersSent :
                self._mws2.Log( 'No response was sent from route %s.'
                                % self._routeResult,
                                self._mws2.WARNING )
                currentResp.ReturnNotImplemented()
        except Exception as ex :
            self._mws2.Log( 'Exception raised from route %s: %s'
                            % (self._routeResult, ex),
                            self._mws2.ERROR )
            currentResp.ReturnInternalServerError()

    # ------------------------------------------------------------------------

    def GetPostedURLEncodedForm(self) :
        res = { }
        if self.ContentType.lower() == 'application/x-www-form-urlencoded' :
            try :
                elements = bytes(self._content).decode('UTF-8').split('&')
                for s in elements :
                    p = s.split('=', 1)
                    if len(p) > 0 :
                        v = (UrlUtils.UnquotePlus(p[1]) if len(p) > 1 else '')
                        res[UrlUtils.UnquotePlus(p[0])] = v
            except :
                pass
        return res

    # ------------------------------------------------------------------------

    def GetPostedJSONObject(self) :
        if self.ContentType.lower() == 'application/json' :
            try :
                s = bytes(self._content).decode('UTF-8')
                return json.loads(s)
            except :
                pass
        return None

    # ------------------------------------------------------------------------

    def GetHeader(self, name) :
        if not isinstance(name, str) or len(name) == 0 :
            raise ValueError('"name" must be a not empty string.')
        return self._headers.get(name.lower(), '')

    # ------------------------------------------------------------------------

    def CheckBasicAuth(self, username, password) :
        if not isinstance(username, str) :
            raise ValueError('"username" must be a string.')
        if not isinstance(password, str) :
            raise ValueError('"password" must be a string.')
        auth = self.Authorization
        if auth :
            try :
                auth = auth.split()
                if len(auth) == 2 and auth[0].lower() == 'basic' :
                    auth = a2b_base64(auth[1].encode()).decode()
                    auth = auth.split(':')
                    return ( auth[0].lower() == username.lower() and \
                             auth[1] == password )
            except :
                pass
        return False

    # ------------------------------------------------------------------------

    def CheckBearerAuth(self, token) :
        if not isinstance(token, str) :
            raise ValueError('"token" must be a string.')
        auth = self.Authorization
        if auth :
            try :
                auth = auth.split()
                return ( len(auth) == 2 and \
                         auth[0].lower() == 'bearer' and \
                         auth[1] == token )
            except :
                pass
        return False

    # ------------------------------------------------------------------------

    @property
    def UserAddress(self) :
        return self._xasCli.CliAddr

    # ------------------------------------------------------------------------

    @property
    def IsSSL(self) :
        return self._xasCli.IsSSL

    # ------------------------------------------------------------------------

    @property
    def HttpVer(self) :
        return self._httpVer

    # ------------------------------------------------------------------------

    @property
    def Method(self) :
        return self._method

    # ------------------------------------------------------------------------

    @property
    def Path(self) :
        return self._path

    # ------------------------------------------------------------------------

    @property
    def QueryString(self) :
        return self._queryString

    # ------------------------------------------------------------------------

    @property
    def QueryParams(self) :
        return self._queryParams

    # ------------------------------------------------------------------------

    @property
    def Host(self) :
        return self._headers.get('host', '')

    # ------------------------------------------------------------------------

    @property
    def Accept(self) :
        s = self._headers.get('accept', None)
        if s :
            return [x.strip() for x in s.split(',')]
        return [ ]

    # ------------------------------------------------------------------------

    @property
    def AcceptEncodings(self) :
        s = self._headers.get('accept-encoding', None)
        if s :
            return [x.strip() for x in s.split(',')]
        return [ ]

    # ------------------------------------------------------------------------

    @property
    def AcceptLanguages(self) :
        s = self._headers.get('accept-language', None)
        if s :
            return [x.strip() for x in s.split(',')]
        return [ ]

    # ------------------------------------------------------------------------

    @property
    def Cookies(self) :
        s = self._headers.get('cookie', None)
        if s :
            return [x.strip() for x in s.split(';')]
        return [ ]

    # ------------------------------------------------------------------------

    @property
    def CacheControl(self) :
        return self._headers.get('cache-control', '')

    # ------------------------------------------------------------------------

    @property
    def Referer(self) :
        return self._headers.get('referer', '')

    # ------------------------------------------------------------------------

    @property
    def ContentType(self) :
        return self._headers.get('content-type', '').split(';', 1)[0].strip()

    # ------------------------------------------------------------------------

    @property
    def ContentLength(self) :
        try :
            return int(self._headers.get('content-length', 0))
        except :
            return 0

    # ------------------------------------------------------------------------

    @property
    def UserAgent(self) :
        return self._headers.get('user-agent', '')

    # ------------------------------------------------------------------------

    @property
    def Authorization(self) :
        return self._headers.get('authorization', '')

    # ------------------------------------------------------------------------

    @property
    def Origin(self) :
        return self._headers.get('origin', '')

    # ------------------------------------------------------------------------

    @property
    def IsKeepAlive(self) :
        return ('keep-alive' in self._headers.get('connection', '').lower())

    # ------------------------------------------------------------------------

    @property
    def IsUpgrade(self) :
        return ('upgrade' in self._headers.get('connection', '').lower())

    # ------------------------------------------------------------------------

    @property
    def Upgrade(self) :
        return self._headers.get('upgrade', '')

    # ------------------------------------------------------------------------

    @property
    def Content(self) :
        return self._content

    # ------------------------------------------------------------------------

    @property
    def Response(self) :
        return self._response

    # ------------------------------------------------------------------------

    @property
    def XAsyncTCPClient(self) :
        return self._xasCli

# ============================================================================
# ============================================================================
# ============================================================================
