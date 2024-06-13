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

    def GetPostedForm(self) :
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
        elif self.ContentType.lower() == 'multipart/form-data':
            if "boundary=" in self.ContentSubtype.lower():
                msg = "Received multipart form -- processing...."
                self._mws2.Log(msg, self._mws2.DEBUG)
                bound = self.ContentSubtype.split("boundary=")[1].strip()

                msg = "boundary for multipart parts: {}".format(bound)
                self._mws2.Log(msg, self._mws2.DEBUG)

                form_parts = self.__split_parts_at(bound)
                if form_parts:
                    for part in form_parts:
                        res.update(self.__parse_multi_part(part))
                else:
                    self._mws2.Log('Could not split at boundaries', self._mws2.ERROR)
            else:
                self._mws2.Log('Could not find content boundary string', self._mws2.ERROR)
        else:
            self._mws2.Log('GetPostedForm does not support %s' % self.ContentType,
                           self._mws2.ERROR)
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

    def __split_parts_at(self, boundary):
        """ Split multipart/form-data into list with data b/w boundaries. """
        content_bytes = bytes(self._content)
        form_parts = []

        bound_length = len(boundary)
        content_end = len(self._content)
        ind_start = 2
        ind_stop = bound_length + 2

        while ind_stop < content_end:
            # Should always be starting w/ boundary string
            content_chunk = content_bytes[ind_start:ind_stop]
            try:
                content_str = content_chunk.decode('utf-8')
                if content_str != boundary:
                    print("boundary: >>{}<<\ntest_str: >>{}<<".format(
                        boundary, content_str))
                    self._mws2.Log('Ill-formed part of multipart data',
                                   self._mws2.ERROR)
            except Exception as ex:
                self._mws2.Log('Ill-formed part of multipart data: %s' % ex,
                               self._mws2.ERROR)

            # Strip initial \r\n from multipart part
            ind_start = ind_stop + 2

            if ind_start + 2 == content_end:
                # Double-check last four bytes are '--\r\n'
                last_four = content_bytes[ind_start-2:ind_start+2]
                try:
                    end_str = last_four.decode('utf-8')
                except:
                    pass
                if end_str != "--\r\n":
                    self._mws2.Log(
                        'Ill-formed end of multipart msg: %s' % end_str,
                        self._mws2.ERROR)
                break

            # Should have 'Content-Disposition: form-data; name=' next
            ind_stop = ind_start + 38
            test_bytes = content_bytes[ind_stop:ind_stop + bound_length]
            test_str = ""
            is_str = False
            try:
                test_str = test_bytes.decode('utf-8')
                is_str = True
            except:
                pass
            while test_str != boundary:
                ind_stop = ind_stop + 1
                if ind_stop + bound_length > content_end:
                    self._mws2.Log('Cannot find next boundary', self._mws2.ERROR)
                    break
                test_bytes = content_bytes[ind_stop:ind_stop + bound_length]
                try:
                    test_str = test_bytes.decode('utf-8')
                    is_str = True
                except:
                    is_str = False
                    pass
            stop = ind_stop - 4
            form_parts.insert(len(form_parts), content_bytes[ind_start:stop])
            ind_start = ind_stop
            ind_stop = ind_stop + bound_length
        return form_parts

    # ------------------------------------------------------------------------

    def __parse_multi_part(self, form_data):
        """
        Extract content from multipart/form-data.
        Argument form_data is content between boundaries (i.e. an item from
        list returned by __extract_form_parts() above).
        """
        all_text = False
        try:
            form_str = form_data.decode('utf-8')
            all_text = True
        except:
            pass
        if all_text:
            return self.__parse_multi_text(form_str)

        ret_dict = {}

        # Separate header text from binary file data.
        disp_str = "Content-Disposition: form-data; "
        str_start = 0
        str_end = len(disp_str)
        header_str = form_data[str_start:str_end].decode('utf-8')
        while not header_str.endswith("\r\n\r\n"):
            str_end = str_end + 1
            header_str = form_data[str_start:str_end].decode('utf-8')
        header_str = header_str[len(disp_str):].strip()
        tmp_dict = self.__parse_upload_header(header_str)

        # Save to drive.
        # TODO: Should sanitize the filename in case of malicious user.
        if "name" in tmp_dict and "filename" in tmp_dict:
            ret_dict[tmp_dict["name"]] = tmp_dict["filename"]
            upload_dir = self._mws2._uploadPath
            ret_dict["saved_as"] = "{}/{}".format(upload_dir, tmp_dict["filename"])
            with open(ret_dict["saved_as"], "wb") as bin_fh:
                bin_fh.write(form_data[str_end:])
            self._mws2.Log('ret_dict: %s' % ret_dict, self._mws2.DEBUG)
        else:
            self._mws2.Log('Cannot parse: %s' % header_str, self._mws2.ERROR)

        return ret_dict

    # ------------------------------------------------------------------------

    def __parse_multi_text(self, form_str):
        """
        Extract content from multipart/form-data.
        Argument form_str is decoded (utf-8) content between boundaries.
        """
        # First line should at least have content-disposition and name.
        ret_dict = {}
        header_content = form_str.split("\r\n\r\n")
        disp_str = "Content-Disposition: form-data; "
        header = header_content[0].split(disp_str)[1]

        if "filename" in header:
            tmp_dict = self.__parse_upload_header(header)
            if "name" in tmp_dict and "filename" in tmp_dict:
                ret_dict[tmp_dict["name"]] = tmp_dict["filename"]
                ret_dict[tmp_dict["filename"]] = header_content[1]
            else:
                self._mws2.Log('Cannot parse: %s' % header,
                            self._mws2.ERROR)
        else:
            header_parts = header.split("=")
            if len(header_parts) > 2:
                self._mws2.Log('Ill-formed multipart part header: %s' % header,
                            self._mws2.ERROR)
            else:
                dict_key = header_parts[1].replace('"', '')
                ret_dict[dict_key] = header_content[1]

        return ret_dict

    # ------------------------------------------------------------------------

    def __parse_upload_header(self, header):
        """ Parse header from multipart/form-data into dictionary. """
        header_lines = header.split("\r\n")
        header_parts = header_lines[0].split("; ")
        tmp_dict = {}
        for part in header_parts:
            print("\t{}".format(part))
            part_items = part.split("=")
            tmp_dict[part_items[0]] = part_items[1].replace('"', '')
        return tmp_dict

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
    def ContentSubtype(self):
        return self._headers.get('content-type', '').split(';', 1)[1].strip()

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
