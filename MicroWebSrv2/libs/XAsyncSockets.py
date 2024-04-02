"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""


from   _thread  import allocate_lock, start_new_thread, stack_size
from   time     import sleep
from   select   import select
import socket
import ssl

try :
    from time import perf_counter
except :
    from time import ticks_ms
    def perf_counter() :
        return ticks_ms() / 1000

# ============================================================================
# ===( XAsyncSocketsPool )====================================================
# ============================================================================

class XAsyncSocketsPoolException(Exception) :
    pass

class XAsyncSocketsPool :

    _CHECK_SEC_INTERVAL = 1.0

    def __init__(self) :
        self._processing   = None
        self._microWorkers = None
        self._opLock       = allocate_lock()
        self._asyncSockets = { }
        self._readList     = [ ]
        self._writeList    = [ ]
        self._handlingList = [ ]
        self._udpSockEvt   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for i in range(30) :
            self._udpSockEvtAddr = ('127.0.0.1', 54321+i)
            try :
                self._udpSockEvt.bind(self._udpSockEvtAddr)
                break
            except :
                pass

    # ------------------------------------------------------------------------

    def _addSocket(self, socket, asyncSocket) :
        if socket and asyncSocket :
            with self._opLock :
                if socket not in self._asyncSockets :
                    self._asyncSockets[socket] = asyncSocket
                    return True
        return False

    # ------------------------------------------------------------------------

    def _removeSocket(self, socket) :
        if socket :
            with self._opLock :
                if socket in self._asyncSockets :
                    del self._asyncSockets[socket]
                if socket in self._readList :
                    self._readList.remove(socket)
                if socket in self._writeList :
                    self._writeList.remove(socket)
                return True
        return False

    # ------------------------------------------------------------------------

    def _socketListAdd(self, socket, socketsList) :
        with self._opLock :
            if socket not in socketsList :
                socketsList.append(socket)
                return True
        return False

    # ------------------------------------------------------------------------

    def _socketListRemove(self, socket, socketsList) :
        with self._opLock :
            if socket in socketsList :
                socketsList.remove(socket)
                return True
        return False

    # ------------------------------------------------------------------------

    def _sendUDPSockEvent(self) :
        self._udpSockEvt.sendto(b'\xFF', self._udpSockEvtAddr)

    # ------------------------------------------------------------------------

    def _processWaitEvents(self) :

        def jobExceptionalCondition(args) :
            if args[0].OnExceptionalCondition() :
                self._removeSocket(args[1])
            self._socketListRemove(args[1], self._handlingList)

        def jobReadyForWriting(args) :
            if args[0].OnReadyForWriting() :
                self._removeSocket(args[1])
            self._socketListRemove(args[1], self._handlingList)

        def jobReadyForReading(args) :
            if args[0].OnReadyForReading() :
                self._removeSocket(args[1])
            self._socketListRemove(args[1], self._handlingList)

        self._processing = True
        
        self._socketListAdd(self._udpSockEvt, self._readList)

        timeSec       = perf_counter()
        udpSockEvtBuf = bytearray(32)
        
        while self._processing :
            try :
                try :
                    rd, wr, ex = select( self._readList,
                                         self._writeList,
                                         self._readList,
                                         XAsyncSocketsPool._CHECK_SEC_INTERVAL )
                except KeyboardInterrupt :
                    break
                except :
                    sleep(XAsyncSocketsPool._CHECK_SEC_INTERVAL)
                    continue
                if not self._processing :
                    break
                for socketsList in ex, wr, rd :
                    for sock in socketsList :
                        if sock == self._udpSockEvt :
                            self._udpSockEvt.recv_into(udpSockEvtBuf)
                        else :
                            asyncSocket = self._asyncSockets.get(sock)
                            if asyncSocket and asyncSocket.GetSocketObj() == sock and sock.fileno() != -1 :
                                if self._socketListAdd(sock, self._handlingList) :
                                    if socketsList is rd :
                                        if self._microWorkers :
                                            self._microWorkers.AddJob(jobReadyForReading, (asyncSocket, sock))
                                        else :
                                            jobReadyForReading((asyncSocket, sock))
                                    elif socketsList is wr :
                                        self._socketListRemove(sock, self._writeList)
                                        if self._microWorkers :
                                            self._microWorkers.AddJob(jobReadyForWriting, (asyncSocket, sock))
                                        else :
                                            jobReadyForWriting((asyncSocket, sock))
                                    else :
                                        self._removeSocket(sock)
                                        if self._microWorkers :
                                            self._microWorkers.AddJob(jobExceptionalCondition, (asyncSocket, sock))
                                        else :
                                            jobExceptionalCondition((asyncSocket, sock))
                            else :
                                self._removeSocket(sock)
                                sock.close()
                sec = perf_counter()
                if sec > timeSec + XAsyncSocketsPool._CHECK_SEC_INTERVAL :
                    timeSec = sec
                    for asyncSocket in list(self._asyncSockets.values()) :
                        if asyncSocket.ExpireTimeSec and \
                           timeSec > asyncSocket.ExpireTimeSec :
                            asyncSocket._close(XClosedReason.Timeout)
            except :
                pass

        if self._microWorkers :
            self._microWorkers.StopAll()
            self._microWorkers = None
        for asyncSocket in list(self._asyncSockets.values()) :
            try :
                asyncSocket.Close()
            except :
                pass

        self._readList.clear()
        self._writeList.clear()

        self._processing = None

    # ------------------------------------------------------------------------

    def AddAsyncSocket(self, asyncSocket) :
        try :
            socket = asyncSocket.GetSocketObj()
        except :
            raise XAsyncSocketsPoolException('AddAsyncSocket : "asyncSocket" is incorrect.')
        return self._addSocket(socket, asyncSocket)

    # ------------------------------------------------------------------------

    def RemoveAsyncSocket(self, asyncSocket) :
        try :
            socket = asyncSocket.GetSocketObj()
        except :
            raise XAsyncSocketsPoolException('RemoveAsyncSocket : "asyncSocket" is incorrect.')
        return self._removeSocket(socket)

    # ------------------------------------------------------------------------

    def GetAllAsyncSockets(self) :
        return list(self._asyncSockets.values())

    # ------------------------------------------------------------------------

    def GetAsyncSocketByID(self, id) :
        return self._asyncSockets.get(id, None)

    # ------------------------------------------------------------------------

    def NotifyNextReadyForReading(self, asyncSocket, notify) :
        try :
            socket = asyncSocket.GetSocketObj()
        except :
            raise XAsyncSocketsPoolException('NotifyNextReadyForReading : "asyncSocket" is incorrect.')
        if notify :
            if self._socketListAdd(socket, self._readList) :
                self._sendUDPSockEvent()
        else :
            self._socketListRemove(socket, self._readList)

    # ------------------------------------------------------------------------

    def NotifyNextReadyForWriting(self, asyncSocket, notify) :
        try :
            socket = asyncSocket.GetSocketObj()
        except :
            raise XAsyncSocketsPoolException('NotifyNextReadyForWriting : "asyncSocket" is incorrect.')
        if notify :
            if self._socketListAdd(socket, self._writeList) :
                self._sendUDPSockEvent()
        else :
            self._socketListRemove(socket, self._writeList)

    # ------------------------------------------------------------------------

    def AsyncWaitEvents(self, threadsCount=0) :
        if self.WaitEventsProcessing :
            return
        self._processing = False
        if threadsCount > 0 :
            try :
                if threadsCount > 1 :
                    self._microWorkers = MicroWorkers(workersCount=threadsCount-1)
                start_new_thread(self._processWaitEvents, ())
                while self._processing != True :
                    sleep(0.010)
            except :
                if self._microWorkers :
                    self._microWorkers.StopAll()
                    self._microWorkers = None
                self._processing = None
                raise XAsyncSocketsPoolException('AsyncWaitEvents : Fatal error to create new threads...')
        else :
            self._processWaitEvents()

    # ------------------------------------------------------------------------

    def StopWaitEvents(self) :
        if not self.WaitEventsProcessing :
            return
        self._processing = False
        self._sendUDPSockEvent()
        while self.WaitEventsProcessing :
            sleep(0.010)

    # ------------------------------------------------------------------------

    @property
    def WaitEventsProcessing(self) :
        return (self._processing is not None)

# ============================================================================
# ===( XClosedReason )========================================================
# ============================================================================

class XClosedReason() :

    Error        = 0x00
    ClosedByHost = 0x01
    ClosedByPeer = 0x02
    Timeout      = 0x03

# ============================================================================
# ===( XAsyncSocket )=========================================================
# ============================================================================

class XAsyncSocketException(Exception) :
    pass

class XAsyncSocket :

    def __init__(self, asyncSocketsPool, socket, recvBufSlot=None, sendBufSlot=None) :
        if type(self) is XAsyncSocket :
            raise XAsyncSocketException('XAsyncSocket is an abstract class and must be implemented.')
        self._asyncSocketsPool = asyncSocketsPool
        self._socket           = socket
        self._recvBufSlot      = recvBufSlot
        self._sendBufSlot      = sendBufSlot
        self._expireTimeSec    = None
        self._state            = None
        self._onClosed         = None
        try :
            socket.settimeout(0)
            socket.setblocking(0)
            if (recvBufSlot is not None and type(recvBufSlot) is not XBufferSlot) or \
               (sendBufSlot is not None and type(sendBufSlot) is not XBufferSlot) :
                raise Exception()
            asyncSocketsPool.AddAsyncSocket(self)
        except :
            raise XAsyncSocketException('XAsyncSocket : Arguments are incorrects.')

    # ------------------------------------------------------------------------

    def _setExpireTimeout(self, timeoutSec) :
        try :
            if timeoutSec and timeoutSec > 0 :
                self._expireTimeSec = perf_counter() + timeoutSec
        except :
            raise XAsyncSocketException('"timeoutSec" is incorrect to set expire timeout.')

    # ------------------------------------------------------------------------

    def _removeExpireTimeout(self) :
        self._expireTimeSec = None

    # ------------------------------------------------------------------------

    def _close(self, closedReason=XClosedReason.Error, triggerOnClosed=True) :
        if self._asyncSocketsPool.RemoveAsyncSocket(self) :
            try :
                self._socket.close()
            except :
                pass
            if self._recvBufSlot is not None :
                self._recvBufSlot.Available = True
                self._recvBufSlot = None
            if self._sendBufSlot is not None :
                self._sendBufSlot.Available = True
                self._sendBufSlot = None
            if triggerOnClosed and self._onClosed :
                try :
                    self._onClosed(self, closedReason)
                except Exception as ex :
                    raise XAsyncSocketException('Error when handling the "OnClose" event : %s' % ex)
            return True
        return False

    # ------------------------------------------------------------------------

    def GetAsyncSocketsPool(self) :
        return self._asyncSocketsPool

    # ------------------------------------------------------------------------

    def GetSocketObj(self) :
        return self._socket

    # ------------------------------------------------------------------------

    def Close(self) :
        return self._close(XClosedReason.ClosedByHost)

    # ------------------------------------------------------------------------

    def OnReadyForReading(self) :
        return True

    # ------------------------------------------------------------------------

    def OnReadyForWriting(self) :
        return True

    # ------------------------------------------------------------------------

    def OnExceptionalCondition(self) :
        self._close()
        return True

    # ------------------------------------------------------------------------

    @property
    def SocketID(self) :
        return self._socket.fileno() if self._socket else None

    @property
    def ExpireTimeSec(self) :
        return self._expireTimeSec

    @property
    def OnClosed(self) :
        return self._onClosed
    @OnClosed.setter
    def OnClosed(self, value) :
        self._onClosed = value

    @property
    def State(self) :
        return self._state
    @State.setter
    def State(self, value) :
        self._state = value

# ============================================================================
# ===( XAsyncTCPServer )======================================================
# ============================================================================

class XAsyncTCPServerException(Exception) :
    pass

class XAsyncTCPServer(XAsyncSocket) :

    @staticmethod
    def Create(asyncSocketsPool, srvAddr, srvBacklog=256, bufSlots=None) :
        try :
            srvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except :
            raise XAsyncTCPServerException('Create : Cannot open socket (no enought memory).')
        try :
            srvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srvSocket.bind(srvAddr)
            srvSocket.listen(srvBacklog)
        except :
            raise XAsyncTCPServerException('Create : Error to binding the TCP server on this address.')
        if not bufSlots :
            bufSlots = XBufferSlots(256, 4096, keepAlloc=True)
        xAsyncTCPServer = XAsyncTCPServer( asyncSocketsPool,
                                           srvSocket,
                                           srvAddr,
                                           bufSlots )
        asyncSocketsPool.NotifyNextReadyForReading(xAsyncTCPServer, True)
        return xAsyncTCPServer

    # ------------------------------------------------------------------------

    def __init__(self, asyncSocketsPool, srvSocket, srvAddr, bufSlots) :
        try :
            super().__init__(asyncSocketsPool, srvSocket)
            self._srvAddr          = srvAddr
            self._bufSlots         = bufSlots
            self._onClientAccepted = None
        except :
            raise XAsyncTCPServerException('Error to creating XAsyncTCPServer, arguments are incorrects.')

    # ------------------------------------------------------------------------

    def OnReadyForReading(self) :
        try :
            cliSocket, cliAddr = self._socket.accept()
        except :
            return
        recvBufSlot = self._bufSlots.GetAvailableSlot()
        sendBufSlot = self._bufSlots.GetAvailableSlot()
        if not recvBufSlot or not sendBufSlot or not self._onClientAccepted :
            if recvBufSlot :
                recvBufSlot.Available = True
            if sendBufSlot :
                sendBufSlot.Available = True
            cliSocket.close()
            return
        asyncTCPCli = XAsyncTCPClient( self._asyncSocketsPool,
                                       cliSocket,
                                       self._srvAddr,
                                       cliAddr,
                                       recvBufSlot,
                                       sendBufSlot )
        try :
            self._onClientAccepted(self, asyncTCPCli)
        except Exception as ex :
            asyncTCPCli._close()
            raise XAsyncTCPServerException('Error when handling the "OnClientAccepted" event : %s' % ex)

    # ------------------------------------------------------------------------

    @property
    def SrvAddr(self) :
        return self._srvAddr

    @property
    def OnClientAccepted(self) :
        return self._onClientAccepted
    @OnClientAccepted.setter
    def OnClientAccepted(self, value) :
        self._onClientAccepted = value

# ============================================================================
# ===( XAsyncTCPClient )======================================================
# ============================================================================

class XAsyncTCPClientException(Exception) :
    pass

class XAsyncTCPClient(XAsyncSocket) :

    @staticmethod
    def Create( asyncSocketsPool,
                srvAddr,
                connectTimeout = 5,
                recvBufLen     = 4096,
                sendBufLen     = 4096,
                connectAsync   = True ) :
        try :
            size        = max(256, recvBufLen)
            recvBufSlot = XBufferSlot(size=size, keepAlloc=True)
            size        = max(256, sendBufLen)
            sendBufSlot = XBufferSlot(size=size, keepAlloc=True)
        except :
            raise XAsyncTCPClientException('Create : Out of memory?')
        try :
            cliSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except :
            raise XAsyncTCPClientException('Create : Cannot open socket (no enought memory).')
        asyncTCPCli = XAsyncTCPClient( asyncSocketsPool,
                                       cliSocket,
                                       srvAddr,
                                       None,
                                       recvBufSlot,
                                       sendBufSlot )
        ok = False
        try :
            if connectAsync and hasattr(cliSocket, 'connect_ex') :
                errno = cliSocket.connect_ex(srvAddr)
                if errno == 0 or errno == 36 :
                    asyncTCPCli._setExpireTimeout(connectTimeout)
                    ok = True
            else :
                try :
                    addr = socket.getaddrinfo( srvAddr[0],
                                               srvAddr[1],
                                               socket.AF_INET )
                except :
                    addr = socket.getaddrinfo( srvAddr[0],
                                               srvAddr[1] )
                addr = addr[0][-1]
                if connectAsync :
                    asyncTCPCli._setExpireTimeout(connectTimeout)
                else :
                    cliSocket.settimeout(connectTimeout)
                    cliSocket.setblocking(1)
                try :
                    cliSocket.connect(srvAddr)
                except OSError as ex :
                    if not connectAsync or str(ex) != '119' :
                        raise ex
                if not connectAsync :
                    cliSocket.settimeout(0)
                    cliSocket.setblocking(0)
                ok = True
        except :
            pass
        if ok :
            asyncSocketsPool.NotifyNextReadyForWriting(asyncTCPCli, True)
            return asyncTCPCli
        asyncTCPCli._close()
        return None

    # ------------------------------------------------------------------------

    def __init__(self, asyncSocketsPool, cliSocket, srvAddr, cliAddr, recvBufSlot, sendBufSlot) :
        try :
            super().__init__(asyncSocketsPool, cliSocket, recvBufSlot, sendBufSlot)
            self._srvAddr          = srvAddr
            self._cliAddr          = cliAddr if cliAddr else ('0.0.0.0', 0)
            self._onFailsToConnect = None
            self._onConnected      = None
            self._onDataRecv       = None
            self._onDataRecvArg    = None
            self._onDataSent       = None
            self._onDataSentArg    = None
            self._sizeToRecv       = None
            self._rdLinePos        = None
            self._rdLineEncoding   = None
            self._rdBufView        = None
            self._wrBufView        = None
            self._socketOpened     = (cliAddr is not None)
        except :
            raise XAsyncTCPClientException('Error to creating XAsyncTCPClient, arguments are incorrects.')

    # ------------------------------------------------------------------------

    def Close(self) :
        if self._wrBufView :
            try :
                self._socket.send(self._wrBufView)
            except :
                pass
        try :
            self._socket.shutdown(socket.SHUT_RDWR)
        except :
            pass
        return self._close(XClosedReason.ClosedByHost)

    # ------------------------------------------------------------------------

    def OnReadyForReading(self) :
        while True :
            if self._rdLinePos is not None :
                # In the context of reading a line,
                while True :
                    try :
                        try :
                            b = self._socket.recv(1)
                        except ssl.SSLError as sslErr :
                            if sslErr.args[0] != ssl.SSL_ERROR_WANT_READ :
                                self._close()
                            return
                        except BlockingIOError as bioErr :
                            if bioErr.errno != 35 :
                                self._close()
                            return
                        except :
                            self._close()
                            return
                    except :
                        self._close()
                        return
                    if b :
                        if b == b'\n' :
                            lineLen = self._rdLinePos 
                            self._rdLinePos = None
                            self._asyncSocketsPool.NotifyNextReadyForReading(self, False)
                            self._removeExpireTimeout()
                            if self._onDataRecv :
                                line = self._recvBufSlot.Buffer[:lineLen]
                                try :
                                    line = bytes(line).decode(self._rdLineEncoding)
                                except :
                                    line = None
                                try :
                                    self._onDataRecv(self, line, self._onDataRecvArg)
                                except Exception as ex :
                                    raise XAsyncTCPClientException('Error when handling the "OnDataRecv" event : %s' % ex)
                            if self.IsSSL and self._socket.pending() > 0 :
                                break
                            return
                        elif b != b'\r' :
                            try :
                                if self._rdLinePos < self._recvBufSlot.Size :
                                    self._recvBufSlot.Buffer[self._rdLinePos] = ord(b)
                                    self._rdLinePos += 1
                                else :
                                    self._close()
                                    return
                            except :
                                return
                    else :
                        self._close(XClosedReason.ClosedByPeer)
                        return
            elif self._sizeToRecv :
                # In the context of reading data,
                recvBuf = self._rdBufView[-self._sizeToRecv:]
                try :
                    try :
                        n = self._socket.recv_into(recvBuf)
                    except ssl.SSLError as sslErr :
                        if sslErr.args[0] != ssl.SSL_ERROR_WANT_READ :
                            self._close()
                        return
                    except BlockingIOError as bioErr :
                        if bioErr.errno != 35 :
                            self._close()
                        return
                    except :
                        self._close()
                        return
                except :
                    try :
                        n = self._socket.readinto(recvBuf)
                    except :
                        self._close()
                        return
                if not n :
                    self._close(XClosedReason.ClosedByPeer)
                    return
                self._sizeToRecv -= n
                if not self._sizeToRecv :
                    data = self._rdBufView
                    self._rdBufView = None
                    self._asyncSocketsPool.NotifyNextReadyForReading(self, False)
                    self._removeExpireTimeout()
                    if self._onDataRecv :
                        try :
                            self._onDataRecv(self, data, self._onDataRecvArg)
                        except Exception as ex :
                            raise XAsyncTCPClientException('Error when handling the "OnDataRecv" event : %s' % ex)
                    if not self.IsSSL or self._socket.pending() == 0 :
                        return
            else :
                self._close(XClosedReason.ClosedByHost)
                return True

    # ------------------------------------------------------------------------

    def OnReadyForWriting(self) :
        if not self._socketOpened :
            if hasattr(self._socket, "getsockopt") :
                if self._socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) :
                    self._close(XClosedReason.Error, triggerOnClosed=False)
                    if self._onFailsToConnect :
                        try :
                            self._onFailsToConnect(self)
                        except Exception as ex :
                            raise XAsyncTCPClientException('Error when handling the "OnFailsToConnect" event : %s' % ex)
                    return
                self._cliAddr = self._socket.getsockname()
                self._removeExpireTimeout()
            self._socketOpened = True
            if self._onConnected :
                try :
                    self._onConnected(self)
                except Exception as ex :
                    raise XAsyncTCPClientException('Error when handling the "OnConnected" event : %s' % ex)
            return
        if self._wrBufView :
            try :
                n = self._socket.send(self._wrBufView)
            except Exception as ex :
                if hasattr(ssl, 'SSLEOFError') and isinstance(ex, ssl.SSLEOFError) :
                    self._close()
                    return True
                else :
                    self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
                    return
            self._wrBufView = self._wrBufView[n:]
            if self._wrBufView :
                self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
            elif self._onDataSent :
                try :
                    self._onDataSent(self, self._onDataSentArg)
                except Exception as ex :
                    raise XAsyncTCPClientException('Error when handling the "OnDataSent" event : %s' % ex)

    # ------------------------------------------------------------------------

    def AsyncRecvLine(self, lineEncoding='UTF-8', onLineRecv=None, onLineRecvArg=None, timeoutSec=None) :
        if self._rdLinePos is not None or self._sizeToRecv :
            raise XAsyncTCPClientException('AsyncRecvLine : Already waiting asynchronous receive.')
        if self._socket :
            self._setExpireTimeout(timeoutSec)
            self._rdLinePos      = 0
            self._rdLineEncoding = lineEncoding
            self._onDataRecv     = onLineRecv
            self._onDataRecvArg  = onLineRecvArg
            self._asyncSocketsPool.NotifyNextReadyForReading(self, True)
            return True
        return False

    # ------------------------------------------------------------------------

    def AsyncRecvData(self, size=None, onDataRecv=None, onDataRecvArg=None, timeoutSec=None) :
        if self._rdLinePos is not None or self._sizeToRecv :
            raise XAsyncTCPClientException('AsyncRecvData : Already waiting asynchronous receive.')
        if self._socket :
            if size is None :
                size = self._recvBufSlot.Size
            elif not isinstance(size, int) or size <= 0 :
                raise XAsyncTCPClientException('AsyncRecvData : "size" is incorrect.')
            if size <= self._recvBufSlot.Size :
                self._rdBufView = memoryview(self._recvBufSlot.Buffer)[:size]
            else :
                try :
                    self._rdBufView = memoryview(bytearray(size))
                except :
                    raise XAsyncTCPClientException('AsyncRecvData : No enought memory to receive %s bytes.' % size)
            self._setExpireTimeout(timeoutSec)
            self._sizeToRecv    = size
            self._onDataRecv    = onDataRecv
            self._onDataRecvArg = onDataRecvArg
            self._asyncSocketsPool.NotifyNextReadyForReading(self, True)
            return True
        return False

    # ------------------------------------------------------------------------

    def AsyncSendData(self, data, onDataSent=None, onDataSentArg=None) :
        if self._socket :
            try :
                if bytes([data[0]]) :
                    if self._wrBufView :
                        self._wrBufView = memoryview(bytes(self._wrBufView) + data)
                    else :
                        self._wrBufView = memoryview(data)
                    self._onDataSent    = onDataSent
                    self._onDataSentArg = onDataSentArg
                    self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
                    return True
            except :
                pass
            raise XAsyncTCPClientException('AsyncSendData : "data" is incorrect.')
        return False

    # ------------------------------------------------------------------------

    def AsyncSendSendingBuffer(self, size=None, onDataSent=None, onDataSentArg=None) :
        if self._wrBufView :
            raise XAsyncTCPClientException('AsyncSendBufferSlot : Already waiting to send data.')
        if self._socket :
            if size is None :
                size = self._sendBufSlot.Size
            if size > 0 and size <= self._sendBufSlot.Size :
                self._wrBufView     = memoryview(self._sendBufSlot.Buffer)[:size]
                self._onDataSent    = onDataSent
                self._onDataSentArg = onDataSentArg
                self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
                return True
        return False

    # ------------------------------------------------------------------------

    def _doSSLHandshake(self) :
        count = 0
        while count < 10 :
            try :
                self._socket.do_handshake()
                break
            except ssl.SSLError as sslErr :
                count += 1
                if sslErr.args[0] == ssl.SSL_ERROR_WANT_READ :
                    select([self._socket], [], [], 1)
                elif sslErr.args[0] == ssl.SSL_ERROR_WANT_WRITE :
                    select([], [self._socket], [], 1)
                else :
                    raise XAsyncTCPClientException('SSL : Bad handshake : %s' % sslErr)
            except Exception as ex :
                raise XAsyncTCPClientException('SSL : Handshake error : %s' % ex)
        else :
            raise XAsyncTCPClientException('SSL : Handshake error')

    # ------------------------------------------------------------------------

    def StartSSL( self,
                  keyfile     = None,
                  certfile    = None,
                  server_side = False,
                  cert_reqs   = 0,
                  ca_certs    = None ) :
        if not hasattr(ssl, 'SSLContext') :
            raise XAsyncTCPClientException('StartSSL : This SSL implementation is not supported.')
        if self.IsSSL :
            raise XAsyncTCPClientException('StartSSL : SSL already started.')
        try :
            self._asyncSocketsPool.NotifyNextReadyForWriting(self, False)
            self._asyncSocketsPool.NotifyNextReadyForReading(self, False)
            self._asyncSocketsPool.RemoveAsyncSocket(self)
            self._socket = ssl.wrap_socket( self._socket,
                                            keyfile     = keyfile,
                                            certfile    = certfile,
                                            server_side = server_side,
                                            cert_reqs   = cert_reqs,
                                            ca_certs    = ca_certs,
                                            do_handshake_on_connect = False )
            self._asyncSocketsPool.AddAsyncSocket(self)
        except Exception as ex :
            raise XAsyncTCPClientException('StartSSL : %s' % ex)
        self._doSSLHandshake()

    # ------------------------------------------------------------------------

    def StartSSLContext(self, sslContext, serverSide=False) :
        if not hasattr(ssl, 'SSLContext') :
            raise XAsyncTCPClientException('StartSSLContext : This SSL implementation is not supported.')
        if not isinstance(sslContext, ssl.SSLContext) :
            raise XAsyncTCPClientException('StartSSLContext : "sslContext" is incorrect.')
        if self.IsSSL :
            raise XAsyncTCPClientException('StartSSLContext : SSL already started.')
        try :
            self._asyncSocketsPool.NotifyNextReadyForWriting(self, False)
            self._asyncSocketsPool.NotifyNextReadyForReading(self, False)
            self._asyncSocketsPool.RemoveAsyncSocket(self)
            self._socket = sslContext.wrap_socket( self._socket,
                                                   server_side             = serverSide,
                                                   do_handshake_on_connect = False )
            self._asyncSocketsPool.AddAsyncSocket(self)
        except Exception as ex :
            raise XAsyncTCPClientException('StartSSLContext : %s' % ex)
        self._doSSLHandshake()

    # ------------------------------------------------------------------------

    @property
    def SrvAddr(self) :
        return self._srvAddr

    @property
    def CliAddr(self) :
        return self._cliAddr

    @property
    def IsSSL(self) :
        return ( hasattr(ssl, 'SSLContext') and \
                 hasattr(ssl, 'SSLSocket')  and \
                 isinstance(self._socket, ssl.SSLSocket) )

    @property
    def SendingBuffer(self) :
        return self._sendBufSlot.Buffer

    @property
    def OnFailsToConnect(self) :
        return self._onFailsToConnect
    @OnFailsToConnect.setter
    def OnFailsToConnect(self, value) :
        self._onFailsToConnect = value

    @property
    def OnConnected(self) :
        return self._onConnected
    @OnConnected.setter
    def OnConnected(self, value) :
        self._onConnected = value

# ============================================================================
# ===( XAsyncUDPDatagram )====================================================
# ============================================================================

class XAsyncUDPDatagramException(Exception) :
    pass

class XAsyncUDPDatagram(XAsyncSocket) :

    @staticmethod
    def Create(asyncSocketsPool, localAddr=None, recvBufLen=4096, broadcast=False) :
        try :
            udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except :
            raise XAsyncUDPDatagramException('Create : Cannot open socket (no enought memory).')
        if broadcast :
            udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        openRecv = (localAddr is not None)
        if openRecv :
            try :
                udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                udpSocket.bind(localAddr)
            except :
                raise XAsyncUDPDatagramException('Create : Error to binding the UDP Datagram local address.')
            try :
                size        = max(256, recvBufLen)
                recvBufSlot = XBufferSlot(size=size, keepAlloc=False)
            except :
                raise XAsyncUDPDatagramException('Create : Out of memory?')
        else :
            recvBufSlot = None
        xAsyncUDPDatagram = XAsyncUDPDatagram(asyncSocketsPool, udpSocket, recvBufSlot)
        if openRecv :
            asyncSocketsPool.NotifyNextReadyForReading(xAsyncUDPDatagram, True)
        return xAsyncUDPDatagram

    # ------------------------------------------------------------------------

    def __init__(self, asyncSocketsPool, udpSocket, recvBufSlot) :
        try :
            super().__init__(asyncSocketsPool, udpSocket, recvBufSlot, None)
            self._wrDgramFiFo   = XFiFo()
            self._onFailsToSend = None
            self._onDataSent    = None
            self._onDataSentArg = None
            self._onDataRecv    = None
        except :
            raise XAsyncUDPDatagramException('Error to creating XAsyncUDPDatagram, arguments are incorrects.')

    # ------------------------------------------------------------------------

    def OnReadyForReading(self) :
        try :
            n, remoteAddr = self._socket.recvfrom_into(self._recvBufSlot.Buffer)
            datagram      = memoryview(self._recvBufSlot.Buffer)[:n]
        except :
            try :
                buf, remoteAddr = self._socket.recvfrom(self._recvBufSlot.Size)
                datagram        = memoryview(buf)
            except :
                return True
        if self._onDataRecv :
            try :
                self._onDataRecv(self, remoteAddr, datagram)
            except Exception as ex :
                raise XAsyncUDPDatagramException('Error when handling the "OnDataRecv" event : %s' % ex)

    # ------------------------------------------------------------------------

    def OnReadyForWriting(self) :
        if not self._wrDgramFiFo.Empty :
            datagram   = None
            remoteAddr = ('0.0.0.0', 0)
            try :
                datagram, remoteAddr = self._wrDgramFiFo.Get()
                self._socket.sendto(datagram, remoteAddr)
            except :
                if self._onFailsToSend :
                    try :
                        self._onFailsToSend(self, datagram, remoteAddr)
                    except Exception as ex :
                        raise XAsyncUDPDatagramException('Error when handling the "OnFailsToSend" event : %s' % ex)
            if not self._wrDgramFiFo.Empty :
                self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
            if self._onDataSent :
                try :
                    self._onDataSent(self, self._onDataSentArg)
                except Exception as ex :
                    raise XAsyncUDPDatagramException('Error when handling the "OnDataSent" event : %s' % ex)

    # ------------------------------------------------------------------------

    def AsyncSendDatagram(self, datagram, remoteAddr, onDataSent=None, onDataSentArg=None) :
        if self._socket :
            try :
                if bytes([datagram[0]]) and len(remoteAddr) == 2 :
                    self._wrDgramFiFo.Put( (datagram, remoteAddr) )
                    self._onDataSent    = onDataSent
                    self._onDataSentArg = onDataSentArg
                    self._asyncSocketsPool.NotifyNextReadyForWriting(self, True)
                    return True
            except :
                pass
            raise XAsyncUDPDatagramException('AsyncSendDatagram : Arguments are incorrects.')
        return False

    # ------------------------------------------------------------------------

    @property
    def LocalAddr(self) :
        try :
            return self._socket.getsockname()
        except :
            return ('0.0.0.0', 0)

    @property
    def OnDataRecv(self) :
        return self._onDataRecv
    @OnDataRecv.setter
    def OnDataRecv(self, value) :
        self._onDataRecv = value

    @property
    def OnFailsToSend(self) :
        return self._onFailsToSend
    @OnFailsToSend.setter
    def OnFailsToSend(self, value) :
        self._onFailsToSend = value

# ============================================================================
# ===( XBufferSlot )==========================================================
# ============================================================================

class XBufferSlot :

    def __init__(self, size, keepAlloc=True) :
        self._available = True
        self._size      = size
        self._keepAlloc = keepAlloc
        self._buffer    = bytearray(size) if keepAlloc else None

    @property
    def Available(self) :
        return self._available
    @Available.setter
    def Available(self, value) :
        if value and not self._keepAlloc :
            self._buffer = None
        self._available = value

    @property
    def Size(self) :
        return self._size

    @property
    def Buffer(self) :
        self._available = False
        if self._buffer is None :
            self._buffer = bytearray(self._size)
        return self._buffer

# ============================================================================
# ===( XBufferSlots )=========================================================
# ============================================================================

class XBufferSlots :

    def __init__(self, slotsCount, slotsSize, keepAlloc=True) :
        self._slotsCount = slotsCount
        self._slotsSize  = slotsSize
        self._slots      = [ ]
        self._lock       = allocate_lock()
        for i in range(slotsCount) :
            self._slots.append(XBufferSlot(slotsSize, keepAlloc))

    def GetAvailableSlot(self) :
        ret = None
        self._lock.acquire()
        for slot in self._slots :
            if slot.Available :
                slot.Available = False
                ret = slot
                break
        self._lock.release()
        return ret

    @property
    def SlotsCount(self) :
        return self.slotsCount

    @property
    def SlotsSize(self) :
        return self.slotsSize

    @property
    def Slots(self) :
        return self._slots

# ============================================================================
# ===( XFiFo )================================================================
# ============================================================================

class XFiFoException(Exception) :
    pass

class XFiFo :

    def __init__(self) :
        self._lock  = allocate_lock()
        self._first = None
        self._last  = None

    def Put(self, obj) :
        self._lock.acquire()
        if self._first :
            self._last[1] = [obj, None]
            self._last    = self._last[1]
        else :
            self._last  = [obj, None]
            self._first = self._last
        self._lock.release()

    def Get(self) :
        self._lock.acquire()
        if self._first :
            obj         = self._first[0]
            self._first = self._first[1]
            self._lock.release()
            return obj
        else :
            self._lock.release()
            raise XFiFoException('Get : XFiFo is empty.')

    def Clear(self) :
        self._first = None
        self._last  = None

    @property
    def Empty(self) :
        return (self._first is None)

# ============================================================================
# ===( MicroWorkers )=========================================================
# ============================================================================

class MicroWorkersException(Exception) :
    pass

class MicroWorkers :

    def __init__(self, workersCount, workersStackSize=None) :
        self._workersCount = 0
        self._criticalLock = allocate_lock()
        self._workersLock  = allocate_lock()
        self._jobsPrcCount = 0
        self._jobs         = [ ]
        self._processing   = True
        originalStackSize  = None
        if not isinstance(workersCount, int) or workersCount <= 0 :
            raise MicroWorkersException('"workersCount" must be an integer greater than zero.')
        if workersStackSize is not None :
            if not isinstance(workersStackSize, int) or workersStackSize <= 0 :
                raise MicroWorkersException('"workersStackSize" must be an integer greater than zero or None.')
            try :
                originalStackSize = stack_size(workersStackSize)
            except :
                raise MicroWorkersException('"workersStackSize" of %s cannot be used.' % workersStackSize)
        try :
            for _ in range(workersCount) :
                start_new_thread(self._workerThreadFunc, (None, ))
            while self._workersCount < workersCount :
                sleep(0.010)
        except Exception as ex :
            self.StopAll()
            raise MicroWorkersException('Error to create workers : %s' % ex)
        if originalStackSize is not None :
            stack_size(originalStackSize)

    def _workerThreadFunc(self, arg) :
        with self._criticalLock :
            self._workersCount += 1
        while self._processing :
            jobFunc = None
            self._workersLock.acquire()
            if self._processing :
                try :
                    jobFunc, jobArg = self._jobs.pop(0)
                except :
                    self._workersLock.acquire()
            try :
                self._workersLock.release()
            except :
                pass
            if jobFunc :
                with self._criticalLock :
                    self._jobsPrcCount += 1
                try :
                    jobFunc(jobArg)
                except :
                    pass
                with self._criticalLock :
                    self._jobsPrcCount -= 1
        with self._criticalLock :
            self._workersCount -= 1

    def AddJob(self, function, arg=None) :
        if function :
            self._jobs.append( (function, arg) )
            try :
                self._workersLock.release()
            except :
                pass

    def StopAll(self) :
        self._processing = False
        self._jobs.clear()
        try :
            self._workersLock.release()
        except :
            pass
        while self._workersCount :
            sleep(0.010)
            
    @property
    def Count(self) :
        return self._workersCount

    @property
    def JobsInQueue(self) :
        return len(self._jobs)

    @property
    def JobsInProcess(self) :
        return self._jobsPrcCount

    @property
    def IsWorking(self) :
        return (len(self._jobs) > 0 or self._jobsPrcCount > 0)

# ============================================================================
# ============================================================================
# ============================================================================
