
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

from .             import *
from .httpRequest  import HttpRequest
from os            import stat
from sys           import implementation
from _thread       import stack_size

# ============================================================================
# ===( MicroWebSrv2 )=========================================================
# ============================================================================

class MicroWebSrv2Exception(Exception) :
    pass

# ----------------------------------------------------------------------------

class MicroWebSrv2 :

    _DEFAULT_PAGES = [
        "index.html",
        "index.htm",
        "default.html",
        "default.htm"
    ]

    _MIME_TYPES = {
        ".txt"   : "text/plain",
        ".htm"   : "text/html",
        ".html"  : "text/html",
        ".css"   : "text/css",
        ".csv"   : "text/csv",
        ".js"    : "application/javascript",
        ".xml"   : "application/xml",
        ".xhtml" : "application/xhtml+xml",
        ".json"  : "application/json",
        ".zip"   : "application/zip",
        ".pdf"   : "application/pdf",
        ".ts"    : "application/typescript",
        ".woff"  : "font/woff",
        ".woff2" : "font/woff2",
        ".ttf"   : "font/ttf",
        ".otf"   : "font/otf",
        ".jpg"   : "image/jpeg",
        ".jpeg"  : "image/jpeg",
        ".png"   : "image/png",
        ".gif"   : "image/gif",
        ".svg"   : "image/svg+xml",
        ".ico"   : "image/x-icon"
    }

    _HTML_ESCAPE_CHARS = {
        "&" : "&amp;",
        '"' : "&quot;",
        "'" : "&apos;",
        ">" : "&gt;",
        "<" : "&lt;"
    }

    _STAT_MODE_DIR = 1 << 14

    DEBUG        = 0x00
    INFO         = 0x01
    WARNING      = 0x02
    ERROR        = 0x03
    MSG_TYPE_STR = {
        DEBUG   : 'DEBUG',
        INFO    : 'INFO',
        WARNING : 'WARNING',
        ERROR   : 'ERROR'
    }

    # ------------------------------------------------------------------------

    _modules = { }

    # ------------------------------------------------------------------------

    def __init__(self) :
        self._backlog         = None
        self._slotsCount      = None
        self._slotsSize       = None
        self._keepAlloc       = None
        self._maxContentLen   = None
        self._bindAddr        = ('0.0.0.0', 80)
        self._sslContext      = None
        self._rootPath        = 'www'
        self._timeoutSec      = 2
        self._notFoundURL     = None
        self._allowAllOrigins = False
        self._corsAllowAll    = False
        self._onLogging       = None
        self._xasSrv          = None
        self._xasPool         = None
        self.SetNormalConfig()

    # ------------------------------------------------------------------------

    @staticmethod
    def _physPathExists(physPath) :
        try :
            stat(physPath)
            return True
        except :
            return False

    # ------------------------------------------------------------------------

    @staticmethod
    def _physPathIsDir(physPath) :
        return (stat(physPath)[0] & MicroWebSrv2._STAT_MODE_DIR != 0)

    # ------------------------------------------------------------------------

    @staticmethod
    def LoadModule(modName) :
        if not isinstance(modName, str) or len(modName) == 0 :
            raise ValueError('"modName" must be a not empty string.')
        if modName in MicroWebSrv2._modules :
            raise MicroWebSrv2Exception('Module "%s" is already loaded.' % modName)
        try :
            modPath  = MicroWebSrv2.__module__.split('microWebSrv2')[0] \
                     + ('mods.%s' % modName)
            module   = getattr(__import__(modPath).mods, modName)
            modClass = getattr(module, modName)
            if type(modClass) is not type :
                raise Exception
            modInstance = modClass()
            MicroWebSrv2._modules[modName] = modInstance
            return modInstance
        except :
            raise MicroWebSrv2Exception('Cannot load module "%s".' % modName)

    # ------------------------------------------------------------------------

    @staticmethod
    def HTMLEscape(s) :
        if not isinstance(s, str) :
            raise ValueError('"s" must be a string.')
        return ''.join(MicroWebSrv2._HTML_ESCAPE_CHARS.get(c, c) for c in s)

    # ------------------------------------------------------------------------

    @staticmethod
    def AddDefaultPage(filename) :
        if not isinstance(filename, str) or len(filename) == 0 :
            raise ValueError('"filename" must be a not empty string.')
        MicroWebSrv2._DEFAULT_PAGES.append(filename)

    # ------------------------------------------------------------------------

    @staticmethod
    def AddMimeType(ext, mimeType) :
        if not isinstance(ext, str) or len(ext) == 0 :
            raise ValueError('"ext" must be a not empty string.')
        if not isinstance(mimeType, str) or len(mimeType) == 0 :
            raise ValueError('"mimeType" must be a not empty string.')
        MicroWebSrv2._MIME_TYPES[ext.lower()] = mimeType.lower()

    # ------------------------------------------------------------------------

    @staticmethod
    def GetMimeTypeFromFilename(filename) :
        filename = filename.lower()
        for ext in MicroWebSrv2._MIME_TYPES :
            if filename.endswith(ext) :
                return MicroWebSrv2._MIME_TYPES[ext]
        return None

    # ------------------------------------------------------------------------

    def StartInPool(self, asyncSocketsPool) :
        if not isinstance(asyncSocketsPool, XAsyncSocketsPool) :
            raise ValueError('"asyncSocketsPool" must be a XAsyncSocketsPool class.')
        if self._xasSrv :
            raise MicroWebSrv2Exception('Server is already running.')
        try :
            xBufSlots = XBufferSlots( slotsCount = self._slotsCount,
                                      slotsSize  = self._slotsSize,
                                      keepAlloc  = self._keepAlloc )
        except :
            raise MicroWebSrv2Exception('Not enough memory to allocate slots.')
        try :
            self._xasSrv = XAsyncTCPServer.Create( asyncSocketsPool = asyncSocketsPool,
                                                   srvAddr          = self._bindAddr,
                                                   srvBacklog       = self._backlog,
                                                   bufSlots         = xBufSlots )
        except :
            raise MicroWebSrv2Exception('Cannot bind server on %s:%s.' % self._bindAddr)
        self._xasSrv.OnClientAccepted = self._onSrvClientAccepted
        self._xasSrv.OnClosed         = self._onSrvClosed
        self.Log('Server listening on %s:%s.' % self._bindAddr, MicroWebSrv2.INFO)

    # ------------------------------------------------------------------------

    def StartManaged(self, parllProcCount=1, procStackSize=0) :
        if not isinstance(parllProcCount, int) or parllProcCount < 0 :
            raise ValueError('"parllProcCount" must be a positive integer or zero.')
        if not isinstance(procStackSize, int) or procStackSize < 0 :
            raise ValueError('"procStackSize" must be a positive integer or zero.')
        if self._xasSrv :
            raise MicroWebSrv2Exception('Server is already running.')
        if procStackSize == 0 and implementation.name == 'micropython' :
            procStackSize = 8*1024
        try :
            saveStackSize = stack_size(procStackSize)
        except Exception as ex :
            raise ValueError('"procStackSize" of %s is not correct (%s).' % (procStackSize, ex))
        self._xasPool = XAsyncSocketsPool()
        try :
            self.StartInPool(self._xasPool)
            try :
                self.Log('Starts the managed pool to wait for I/O events.', MicroWebSrv2.INFO)
                self._xasPool.AsyncWaitEvents(threadsCount=parllProcCount)
            except :
                raise MicroWebSrv2Exception('Not enough memory to start %s parallel processes.' % parllProcCount)
        except Exception as ex :
            self.Stop()
            raise ex
        finally :
            try :
                stack_size(saveStackSize)
            except :
                pass

    # ------------------------------------------------------------------------

    def Stop(self) :
        if self._xasSrv :
            self._xasSrv.Close()
            self._xasSrv = None
        if self._xasPool :
            self.Log('Stops the managed pool.', MicroWebSrv2.INFO)
            self._xasPool.StopWaitEvents()
            self._xasPool = None

    # ------------------------------------------------------------------------

    def Log(self, msg, msgType) :
        if self._onLogging :
            try :
                self._onLogging(self, str(msg), msgType)
                return
            except Exception as ex :
                msgType = MicroWebSrv2.ERROR
                msg     = 'Exception raised from "OnLoggin" handler: %s' % ex
        t = MicroWebSrv2.MSG_TYPE_STR.get(msgType, None)
        if t :
            print('MWS2-%s> %s' % (t, msg))

    # ------------------------------------------------------------------------

    def ResolvePhysicalPath(self, urlPath) :
        if not isinstance(urlPath, str) or len(urlPath) == 0 :
            raise ValueError('"urlPath" must be a not empty string.')
        try :
            physPath = self._rootPath + urlPath.replace('..', '/')
            if physPath.endswith('/') :
                physPath = physPath[:-1]
            if MicroWebSrv2._physPathIsDir(physPath) :
                for filename in MicroWebSrv2._DEFAULT_PAGES :
                    p = physPath + '/' + filename
                    if MicroWebSrv2._physPathExists(p) :
                        return p
            return physPath
        except :
            return None

    # ------------------------------------------------------------------------

    def _onSrvClientAccepted(self, xAsyncTCPServer, xAsyncTCPClient) :
        if self._sslContext :
            try :
                xAsyncTCPClient.StartSSLContext( sslContext = self._sslContext,
                                                 serverSide = True )
            except :
                self.Log( 'SSL connection failed from %s:%s.'
                          % xAsyncTCPClient.CliAddr,
                          MicroWebSrv2.DEBUG )
                xAsyncTCPClient.Close()
                return
        HttpRequest(self, xAsyncTCPClient)

    # ------------------------------------------------------------------------

    def _onSrvClosed(self, xAsyncTCPServer, closedReason) :
        self.Log('Server %s:%s closed.' % self._bindAddr, MicroWebSrv2.INFO)

    # ------------------------------------------------------------------------

    def _validateChangeConf(self, name='Configuration') :
        if self._xasSrv :
            raise MicroWebSrv2Exception('%s cannot be changed while the server is running.' % name)
    
    # ------------------------------------------------------------------------

    def EnableSSL(self, certFile, keyFile, caFile=None) :
        import ssl
        if not hasattr(ssl, 'SSLContext') :
            raise MicroWebSrv2Exception('Unable to use SSL (implementation not supported).')
        if not isinstance(certFile, str) or len(certFile) == 0 :
            raise ValueError('"certFile" must be a not empty string.')
        if not isinstance(keyFile, str) or len(keyFile) == 0 :
            raise ValueError('"keyFile" must be a not empty string.')
        if caFile is not None and not isinstance(caFile, str) :
            raise ValueError('"caFile" must be a string or None.')
        self._validateChangeConf()
        try :
            ctx = ssl.create_default_context( ssl.Purpose.CLIENT_AUTH,
                                              cafile = caFile )
        except :
            raise ValueError('"caFile" must indicate a valid PEM file.')
        try :
            ctx.load_cert_chain(certfile=certFile, keyfile=keyFile)
        except :
            raise ValueError('"certFile" and "keyFile" must indicate the valid certificate and key files.')
        self._sslContext = ctx
        if self._bindAddr[1] == 80 :
            self._bindAddr = (self._bindAddr[0], 443)

    # ------------------------------------------------------------------------

    def DisableSSL(self) :
        self._validateChangeConf()
        self._sslContext = None
        if self._bindAddr[1] == 443 :
            self._bindAddr = (self._bindAddr[0], 80)

    # ------------------------------------------------------------------------    

    def SetEmbeddedConfig(self) :
        self._validateChangeConf()
        self._backlog       = 8
        self._slotsCount    = 16
        self._slotsSize     = 1024
        self._keepAlloc     = True
        self._maxContentLen = 16*1024

    # ------------------------------------------------------------------------

    def SetLightConfig(self) :
        self._validateChangeConf()
        self._backlog       = 64
        self._slotsCount    = 128
        self._slotsSize     = 1024
        self._keepAlloc     = True
        self._maxContentLen = 512*1024

    # ------------------------------------------------------------------------

    def SetNormalConfig(self) :
        self._validateChangeConf()
        self._backlog       = 256
        self._slotsCount    = 512
        self._slotsSize     = 4*1024
        self._keepAlloc     = True
        self._maxContentLen = 2*1024*1024

    # ------------------------------------------------------------------------

    def SetLargeConfig(self) :
        self._validateChangeConf()
        self._backlog       = 512
        self._slotsCount    = 2048
        self._slotsSize     = 16*1024
        self._keepAlloc     = True
        self._maxContentLen = 8*1024*1024

    # ------------------------------------------------------------------------

    @property
    def IsRunning(self) :
        return ( self._xasPool is not None and \
                 self._xasPool.WaitEventsProcessing and \
                 self._xasSrv is not None )

    # ------------------------------------------------------------------------

    @property
    def ConnQueueCapacity(self) :
        return self._backlog

    @ConnQueueCapacity.setter
    def ConnQueueCapacity(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"ConnQueueCapacity" must be a positive integer.')
        self._validateChangeConf('"ConnQueueCapacity"')
        self._backlog = value

    # ------------------------------------------------------------------------

    @property
    def BufferSlotsCount(self) :
        return self._slotsCount

    @BufferSlotsCount.setter
    def BufferSlotsCount(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"BufferSlotsCount" must be a positive integer.')
        self._validateChangeConf('"BufferSlotsCount"')
        self._slotsCount = value

    # ------------------------------------------------------------------------

    @property
    def BufferSlotSize(self) :
        return self._slotsSize

    @BufferSlotSize.setter
    def BufferSlotSize(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"BufferSlotSize" must be a positive integer.')
        self._validateChangeConf('"BufferSlotSize"')
        self._slotsSize = value

    # ------------------------------------------------------------------------

    @property
    def KeepAllocBufferSlots(self) :
        return self._keepAlloc

    @KeepAllocBufferSlots.setter
    def KeepAllocBufferSlots(self, value) :
        if not isinstance(value, bool) :
            raise ValueError('"KeepAllocBufferSlots" must be a boolean.')
        self._validateChangeConf('"KeepAllocBufferSlots"')
        self._keepAlloc = value

    # ------------------------------------------------------------------------

    @property
    def MaxRequestContentLength(self) :
        return self._maxContentLen

    @MaxRequestContentLength.setter
    def MaxRequestContentLength(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"MaxRequestContentLength" must be a positive integer.')
        self._maxContentLen = value

    # ------------------------------------------------------------------------

    @property
    def BindAddress(self) :
        return self._bindAddr

    @BindAddress.setter
    def BindAddress(self, value) :
        if not value or len(value) != 2  or \
           not isinstance(value[0], str) or \
           not isinstance(value[1], int) :
            raise ValueError('"BindAddress" must be a tuple of (ipAddr, tcpPort).')
        if value[1] < 1 or value[1] > 65535 :
            raise ValueError('"BindAddress" has an incorrect port number.')
        self._validateChangeConf('"BindAddress"')
        self._bindAddr = value

    # ------------------------------------------------------------------------

    @property
    def IsSSLEnabled(self) :
        return (self._sslContext is not None)

    # ------------------------------------------------------------------------

    @property
    def RootPath(self) :
        return self._rootPath

    @RootPath.setter
    def RootPath(self, value) :
        if not isinstance(value, str) or len(value) == 0 :
            raise ValueError('"RootPath" must be a not empty string.')
        self._validateChangeConf('"RootPath"')
        self._rootPath = (value[:-1] if value.endswith('/') else value)

    # ------------------------------------------------------------------------

    @property
    def RequestsTimeoutSec(self) :
        return self._timeoutSec

    @RequestsTimeoutSec.setter
    def RequestsTimeoutSec(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"RequestsTimeoutSec" must be a positive integer.')
        self._timeoutSec = value

    # ------------------------------------------------------------------------

    @property
    def NotFoundURL(self) :
        return self._notFoundURL

    @NotFoundURL.setter
    def NotFoundURL(self, value) :
        if value is not None and not isinstance(value, str) :
            raise ValueError('"NotFoundURL" must be a string or None.')
        self._notFoundURL = value

    # ------------------------------------------------------------------------

    @property
    def AllowAllOrigins(self) :
        return self._allowAllOrigins

    @AllowAllOrigins.setter
    def AllowAllOrigins(self, value) :
        if not isinstance(value, bool) :
            raise ValueError('"AllowAllOrigins" must be a boolean.')
        self._allowAllOrigins = value

    # ------------------------------------------------------------------------

    @property
    def CORSAllowAll(self) :
        return self._corsAllowAll

    @CORSAllowAll.setter
    def CORSAllowAll(self, value) :
        if not isinstance(value, bool) :
            raise ValueError('"CORSAllowAll" must be a boolean.')
        self._corsAllowAll = value

    # ------------------------------------------------------------------------

    @property
    def OnLogging(self) :
        return self._onLogging

    @OnLogging.setter
    def OnLogging(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnLogging" must be a function.')
        self._onLogging = value

# ============================================================================
# ============================================================================
# ============================================================================
