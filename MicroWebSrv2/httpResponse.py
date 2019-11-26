
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

from   os   import stat
import json

# ============================================================================
# ===( HttpResponse )=========================================================
# ============================================================================

class HttpResponse :

    _RESPONSE_CODES = {
        100: ( 'Continue',
               'Request received, please continue.' ),
        101: ( 'Switching Protocols',
               'Switching to new protocol; obey Upgrade header.' ),
        200: ( 'OK',
               'Request fulfilled, document follows.' ),
        201: ( 'Created',
               'Document created, URL follows' ),
        202: ( 'Accepted',
               'Request accepted, processing continues off-line.' ),
        203: ( 'Non-Authoritative Information',
               'Request fulfilled from cache' ),
        204: ( 'No Content',
               'Request fulfilled, nothing follows.' ),
        205: ( 'Reset Content',
               'Clear input form for further input.' ),
        206: ( 'Partial Content',
               'Partial content follows.' ),
        300: ( 'Multiple Choices',
               'Object has several resources -- see URI list.' ),
        301: ( 'Moved Permanently',
               'Object moved permanently -- see URI list.' ),
        302: ( 'Found',
               'Object moved temporarily -- see URI list.' ),
        303: ( 'See Other',
               'Object moved -- see Method and URL list.' ),
        304: ( 'Not Modified',
               'Document has not changed since given time.' ),
        305: ( 'Use Proxy',
               'You must use proxy specified in Location to access this resource.' ),
        307: ( 'Temporary Redirect',
               'Object moved temporarily -- see URI list.' ),
        400: ( 'Bad Request',
               'Bad request syntax or unsupported method.' ),
        401: ( 'Unauthorized',
               'No permission -- see authorization schemes.' ),
        402: ( 'Payment Required',
               'No payment -- see charging schemes.' ),
        403: ( 'Forbidden',
               'Request forbidden -- authorization will not help.' ),
        404: ( 'Not Found',
               'Nothing matches the given URI.' ),
        405: ( 'Method Not Allowed',
               'Specified method is invalid for this resource.' ),
        406: ( 'Not Acceptable',
               'URI not available in preferred format.' ),
        407: ( 'Proxy Authentication Required',
               'You must authenticate with this proxy before proceeding.' ),
        408: ( 'Request Timeout',
               'Request timed out; try again later.' ),
        409: ( 'Conflict',
               'Request conflict.' ),
        410: ( 'Gone',
               'URI no longer exists and has been permanently removed.' ),
        411: ( 'Length Required',
               'Client must specify Content-Length.' ),
        412: ( 'Precondition Failed',
               'Precondition in headers is false.' ),
        413: ( 'Request Entity Too Large',
               'Entity is too large.' ),
        414: ( 'Request-URI Too Long',
               'URI is too long.' ),
        415: ( 'Unsupported Media Type',
               'Entity body in unsupported format.' ),
        416: ( 'Requested Range Not Satisfiable',
               'Cannot satisfy request range.' ),
        417: ( 'Expectation Failed',
               'Expect condition could not be satisfied.' ),
        500: ( 'Internal Server Error',
               'Server got itself in trouble.' ),
        501: ( 'Not Implemented',
               'Server does not support this operation.' ),
        502: ( 'Bad Gateway',
               'Invalid responses from another server/proxy.' ),
        503: ( 'Service Unavailable',
               'The server cannot process the request due to a high load.' ),
        504: ( 'Gateway Timeout',
               'The gateway server did not receive a timely response.' ),
        505: ( 'HTTP Version Not Supported',
               'Cannot fulfill request.' )
    }

    _CODE_CONTENT_TMPL = """\
    <html>
        <head>
            <title>MicroWebSrv2</title>
        </head>
        <body style="font-family: Verdana; background-color: Black; color: White;">
            <h2>MicroWebSrv2 - [%(code)d] %(reason)s</h2>
            %(message)s
        </body>
    </html>
    """

    # ------------------------------------------------------------------------

    def __init__(self, microWebSrv2, request) :
        self._mws2            = microWebSrv2
        self._request         = request
        self._xasCli          = request.XAsyncTCPClient
        self._headers         = { }
        self._allowCaching    = False
        self._acAllowOrigin   = None
        self._contentType     = None
        self._contentCharset  = None
        self._contentLength   = 0
        self._stream          = None
        self._sendingBuf      = None
        self._hdrSent         = False
        self._onSent          = None

    # ------------------------------------------------------------------------

    def SetHeader(self, name, value) :
        if not isinstance(name, str) or len(name) == 0 :
            raise ValueError('"name" must be a not empty string.')
        if value is None :
            raise ValueError('"value" cannot be None.')
        self._headers[name] = str(value)

    # ------------------------------------------------------------------------

    def _onDataSent(self, xasCli, arg) :
        if self._stream :
            try :
                n = self._stream.readinto(self._sendingBuf)
                if n < len(self._sendingBuf) :
                    self._stream.close()
                    self._stream     = None
                    self._sendingBuf = self._sendingBuf[:n]
            except :
                self._xasCli.Close()
                self._mws2.Log( 'Stream cannot be read for request "%s".'
                                % self._request._path,
                                self._mws2.ERROR )
                return
        if self._sendingBuf :
            if self._contentLength :
                self._xasCli.AsyncSendSendingBuffer( size       = len(self._sendingBuf),
                                                     onDataSent = self._onDataSent )
                if not self._stream :
                    self._sendingBuf = None
            else :
                def onChunkHdrSent(xasCli, arg) :
                    def onChunkDataSent(xasCli, arg) :
                        def onLastChunkSent(xasCli, arg) :
                            self._xasCli.AsyncSendData(b'0\r\n\r\n', onDataSent=self._onDataSent)
                        if self._stream :
                            onDataSent = self._onDataSent
                        else :
                            self._sendingBuf = None
                            onDataSent       = onLastChunkSent
                        self._xasCli.AsyncSendData(b'\r\n', onDataSent=onDataSent)
                    self._xasCli.AsyncSendSendingBuffer( size       = len(self._sendingBuf),
                                                         onDataSent = onChunkDataSent )
                data = ('%x\r\n' % len(self._sendingBuf)).encode()
                self._xasCli.AsyncSendData(data, onDataSent=onChunkHdrSent)
        else :
            self._xasCli.OnClosed = None
            if self._keepAlive :
                self._request._waitForRecvRequest()
            else :
                self._xasCli.Close()
            if self._onSent :
                try :
                    self._onSent(self._mws2, self)
                except Exception as ex :
                    self._mws2.Log( 'Exception raised from "Response.OnSent" handler: %s' % ex,
                                    self._mws2.ERROR )

    # ------------------------------------------------------------------------

    def _onClosed(self, xasCli, closedReason) :
        if self._stream :
            try :
                self._stream.close()
            except :
                pass
            self._stream = None
        self._sendingBuf = None

    # ------------------------------------------------------------------------

    def _makeBaseResponseHdr(self, code) :
        reason = self._RESPONSE_CODES.get(code, ('Unknown reason', ))[0]
        self._mws2.Log( 'From %s:%s %s%s %s >> [%s] %s'
                        % ( self._xasCli.CliAddr[0],
                            self._xasCli.CliAddr[1],
                            ('SSL-' if self.IsSSL else ''),
                            self._request._method,
                            self._request._path,
                            code,
                            reason ),
                        self._mws2.DEBUG )
        if self._mws2.AllowAllOrigins :
            self._acAllowOrigin = self._request.Origin
        if self._acAllowOrigin :
            self.SetHeader('Access-Control-Allow-Origin', self._acAllowOrigin)
        self.SetHeader('Server', 'MicroWebSrv2 by JC`zic')
        hdr = ''
        for n in self._headers :
            hdr += '%s: %s\r\n' % (n, self._headers[n])
        resp = 'HTTP/1.1 %s %s\r\n%s\r\n' % (code, reason, hdr)
        return resp.encode('ISO-8859-1')

    # ------------------------------------------------------------------------

    def _makeResponseHdr(self, code) :
        if code >= 200 and code < 300 :
            self._keepAlive = self._request.IsKeepAlive
        else :
            self._keepAlive = False
        if self._keepAlive :
            self.SetHeader('Connection', 'Keep-Alive')
            self.SetHeader('Keep-Alive', 'timeout=%s' % self._mws2._timeoutSec)
        else :
            self.SetHeader('Connection', 'Close')
        if self._allowCaching :
            self.SetHeader('Cache-Control', 'public, max-age=31536000')
        else :
            self.SetHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
        if self._contentType :
            ct = self._contentType
            if self._contentCharset :
                ct += '; charset=%s' % self._contentCharset
            self.SetHeader('Content-Type', ct)
        if self._contentLength :
            self.SetHeader('Content-Length', self._contentLength)
        return self._makeBaseResponseHdr(code)

    # ------------------------------------------------------------------------

    def SwitchingProtocols(self, upgrade) :
        if not isinstance(upgrade, str) or len(upgrade) == 0 :
            raise ValueError('"upgrade" must be a not empty string.')
        if self._hdrSent :
            self._mws2.Log( 'Response headers already sent for request "%s".'
                            % self._request._path,
                            self._mws2.WARNING )
            return
        self.SetHeader('Connection', 'Upgrade')
        self.SetHeader('Upgrade', upgrade)
        data = self._makeBaseResponseHdr(101)
        self._xasCli.AsyncSendData(data)
        self._hdrSent = True

    # ------------------------------------------------------------------------

    def ReturnStream(self, code, stream) :
        if not isinstance(code, int) or code <= 0 :
            raise ValueError('"code" must be a positive integer.')
        if not hasattr(stream, 'readinto') or not hasattr(stream, 'close') :
            raise ValueError('"stream" must be a readable buffer protocol object.')
        if self._hdrSent :
            self._mws2.Log( 'Response headers already sent for request "%s".'
                            % self._request._path,
                            self._mws2.WARNING )
            try :
                stream.close()
            except :
                pass
            return
        if self._request._method != 'HEAD' :
            self._stream          = stream
            self._sendingBuf      = memoryview(self._xasCli.SendingBuffer)
            self._xasCli.OnClosed = self._onClosed
        else :
            try :
                stream.close()
            except :
                pass
        if not self._contentType :
            self._contentType = 'application/octet-stream'
        if not self._contentLength :
            self.SetHeader('Transfer-Encoding', 'chunked')
        data = self._makeResponseHdr(code)
        self._xasCli.AsyncSendData(data, onDataSent=self._onDataSent)
        self._hdrSent = True

    # ------------------------------------------------------------------------

    def Return(self, code, content=None) :
        if not isinstance(code, int) or code <= 0 :
            raise ValueError('"code" must be a positive integer.')
        if self._hdrSent :
            self._mws2.Log( 'Response headers already sent for request "%s".'
                            % self._request._path,
                            self._mws2.WARNING )
            return
        if not content :
            respCode          = self._RESPONSE_CODES.get(code, ('Unknown reason', ''))
            self._contentType = 'text/html'
            content           = self._CODE_CONTENT_TMPL % { 'code'    : code,
                                                            'reason'  : respCode[0],
                                                            'message' : respCode[1] }
        if isinstance(content, str) :
            content = content.encode('UTF-8')
            if not self._contentType :
                self._contentType = 'text/html'
            self._contentCharset = 'UTF-8'
        elif not self._contentType :
            self._contentType = 'application/octet-stream'
        self._contentLength = len(content)
        data = self._makeResponseHdr(code)
        if self._request._method != 'HEAD' :
            data += bytes(content)
        self._xasCli.AsyncSendData(data, onDataSent=self._onDataSent)
        self._hdrSent = True

    # ------------------------------------------------------------------------

    def ReturnJSON(self, code, obj) :
        if not isinstance(code, int) or code <= 0 :
            raise ValueError('"code" must be a positive integer.')
        self._contentType = 'application/json'
        try :
            content = json.dumps(obj)
        except :
            raise ValueError('"obj" cannot be converted into JSON format.')
        self.Return(code, content)

    # ------------------------------------------------------------------------

    def ReturnOk(self, content=None) :
        self.Return(200, content)

    # ------------------------------------------------------------------------

    def ReturnOkJSON(self, obj) :
        self.ReturnJSON(200, obj)

    # ------------------------------------------------------------------------

    def ReturnFile(self, filename, attachmentName=None) :
        if not isinstance(filename, str) or len(filename) == 0 :
            raise ValueError('"filename" must be a not empty string.')
        if attachmentName is not None and not isinstance(attachmentName, str) :
            raise ValueError('"attachmentName" must be a string or None.')
        try :
            size = stat(filename)[6]
        except :
            self.ReturnNotFound()
            return
        try :
            file = open(filename, 'rb')
        except :
            self.ReturnForbidden()
            return
        if attachmentName :
            cd = 'attachment; filename="%s"' % attachmentName.replace('"', "'")
            self.SetHeader('Content-Disposition', cd)
        if not self._contentType :
            self._contentType = self._mws2.GetMimeTypeFromFilename(filename)
        self._contentLength = size
        self.ReturnStream(200, file)

    # ------------------------------------------------------------------------

    def ReturnNotModified(self) :
        self.Return(304)

    # ------------------------------------------------------------------------

    def ReturnRedirect(self, location) :
        if not isinstance(location, str) or len(location) == 0 :
            raise ValueError('"location" must be a not empty string.')
        self.SetHeader('Location', location)
        self.Return(307)

    # ------------------------------------------------------------------------

    def ReturnBadRequest(self) :
        self.Return(400)

    # ------------------------------------------------------------------------

    def ReturnUnauthorized(self, typeName, realm=None) :
        if not isinstance(typeName, str) or len(typeName) == 0 :
            raise ValueError('"typeName" must be a not empty string.')
        if realm is not None and not isinstance(realm, str) :
            raise ValueError('"realm" must be a string or None.')
        wwwAuth = typeName
        if realm :
            wwwAuth += (' realm="%s"' % realm.replace('"', "'")) if realm else ''
        self.SetHeader('WWW-Authenticate', wwwAuth)
        self.Return(401)

    # ------------------------------------------------------------------------

    def ReturnForbidden(self) :
        self.Return(403)

    # ------------------------------------------------------------------------

    def ReturnNotFound(self) :
        if self._mws2._notFoundURL :
            self.ReturnRedirect(self._mws2._notFoundURL)
        else :
            self.Return(404)

    # ------------------------------------------------------------------------

    def ReturnMethodNotAllowed(self) :
        self.Return(405)

    # ------------------------------------------------------------------------

    def ReturnEntityTooLarge(self) :
        self.Return(413)

    # ------------------------------------------------------------------------

    def ReturnInternalServerError(self) :
        self.Return(500)

    # ------------------------------------------------------------------------

    def ReturnNotImplemented(self) :
        self.Return(501)

    # ------------------------------------------------------------------------

    def ReturnServiceUnavailable(self) :
        self.Return(503)

    # ------------------------------------------------------------------------

    def ReturnBasicAuthRequired(self) :
        self.ReturnUnauthorized('Basic')

    # ------------------------------------------------------------------------

    def ReturnBearerAuthRequired(self) :
        self.ReturnUnauthorized('Bearer')

    # ------------------------------------------------------------------------

    @property
    def Request(self) :
        return self._request

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
    def AllowCaching(self) :
        return self._allowCaching

    @AllowCaching.setter
    def AllowCaching(self, value) :
        if not isinstance(value, bool) :
            raise ValueError('"AllowCaching" must be a boolean.')
        self._allowCaching = value

    # ------------------------------------------------------------------------

    @property
    def AccessControlAllowOrigin(self) :
        return self._acAllowOrigin

    @AccessControlAllowOrigin.setter
    def AccessControlAllowOrigin(self, value) :
        if value is not None and not isinstance(value, str) :
            raise ValueError('"AccessControlAllowOrigin" must be a string or None.')
        self._acAllowOrigin = value

    # ------------------------------------------------------------------------

    @property
    def ContentType(self) :
        return self._contentType

    @ContentType.setter
    def ContentType(self, value) :
        if value is not None and not isinstance(value, str) :
            raise ValueError('"ContentType" must be a string or None.')
        self._contentType = value

    # ------------------------------------------------------------------------

    @property
    def ContentCharset(self) :
        return self._contentCharset

    @ContentCharset.setter
    def ContentCharset(self, value) :
        if value is not None and not isinstance(value, str) :
            raise ValueError('"ContentCharset" must be a string or None.')
        self._contentCharset = value

    # ------------------------------------------------------------------------

    @property
    def ContentLength(self) :
        return self._contentLength

    @ContentLength.setter
    def ContentLength(self, value) :
        if not isinstance(value, int) or value < 0 :
            raise ValueError('"ContentLength" must be a positive integer or zero.')
        self._contentLength = value

    # ------------------------------------------------------------------------

    @property
    def HeadersSent(self) :
        return self._hdrSent

    # ------------------------------------------------------------------------

    @property
    def OnSent(self) :
        return self._onSent

    @OnSent.setter
    def OnSent(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnSent" must be a function.')
        self._onSent = value

# ============================================================================
# ============================================================================
# ============================================================================
