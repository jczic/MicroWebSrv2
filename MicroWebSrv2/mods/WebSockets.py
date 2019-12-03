
"""
The MIT License (MIT)
Copyright © 2019 Jean-Christophe Bos & HC² (www.hc2.fr)
"""

from hashlib  import sha1
from binascii import b2a_base64
from struct   import pack

# ============================================================================
# ===( MicroWebSrv2 : WebSockets Module )=====================================
# ============================================================================

class WebSockets :

    _PROTOCOL_VERSION = 13
    _HANDSHAKE_SIGN   = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    # ------------------------------------------------------------------------

    def __init__(self) :
        self._onWebSocketProtocol = None
        self._onWebSocketAccepted = None

    # ------------------------------------------------------------------------

    def OnRequest(self, microWebSrv2, request) :
        if request.IsUpgrade and request.Upgrade.lower() == 'websocket' :
            ver = request.GetHeader('Sec-Websocket-Version')
            if ver == str(WebSockets._PROTOCOL_VERSION) :
                response = request.Response
                key      = request.GetHeader('Sec-Websocket-Key')
                if key :
                    try :
                        key       += WebSockets._HANDSHAKE_SIGN
                        sec        = sha1(key.encode()).digest()
                        sec        = b2a_base64(sec).decode().strip()
                        protocols  = request.GetHeader('Sec-WebSocket-Protocol')
                        response.SetHeader('Sec-WebSocket-Accept', sec)
                        if protocols and self._onWebSocketProtocol :
                            protocols = [x.strip() for x in protocols.split(',')]
                            try :
                                proto = self._onWebSocketProtocol(microWebSrv2, protocols)
                            except Exception as ex :
                                microWebSrv2.Log( 'Exception raised from "WebSockets.OnWebSocketProtocol" handler: %s' % ex,
                                                  microWebSrv2.ERROR )
                                raise ex
                            if proto in protocols :
                                response.SetHeader('Sec-WebSocket-Protocol', proto)
                        response.SwitchingProtocols('websocket')
                        WebSocket(self, microWebSrv2, request)
                    except :
                        response.ReturnInternalServerError()
                else :
                    response.ReturnBadRequest()

    # ------------------------------------------------------------------------

    @property
    def OnWebSocketProtocol(self) :
        return self._onWebSocketProtocol

    @OnWebSocketProtocol.setter
    def OnWebSocketProtocol(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnWebSocketProtocol" must be a function.')
        self._onWebSocketProtocol = value

    # ------------------------------------------------------------------------

    @property
    def OnWebSocketAccepted(self) :
        return self._onWebSocketAccepted

    @OnWebSocketAccepted.setter
    def OnWebSocketAccepted(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnWebSocketAccepted" must be a function.')
        self._onWebSocketAccepted = value

# ============================================================================
# ===( WebSocket )============================================================
# ============================================================================

class WebSocket :

    _OP_FRAME_CONT  = 0x00
    _OP_FRAME_TEXT  = 0x01
    _OP_FRAME_BIN   = 0x02
    _OP_FRAME_CLOSE = 0x08
    _OP_FRAME_PING  = 0x09
    _OP_FRAME_PONG  = 0x0A
    
    _MSG_TYPE_TEXT  = 0x01
    _MSG_TYPE_BIN   = 0x02

    # ------------------------------------------------------------------------

    def __init__(self, wsMod, mws2, request) :

        self._mws2                = mws2
        self._request             = request
        self._xasCli              = request.XAsyncTCPClient
        self._currentMsgType      = None
        self._currentMsgData      = None
        self._isClosed            = False
        self._waitFrameTimeoutSec = 300
        self._maxRecvMsgLen       = mws2.MaxRequestContentLength
        self._onTextMsg           = None
        self._onBinMsg            = None
        self._onClosed            = None

        onWSAccepted    = wsMod.OnWebSocketAccepted

        self._mws2.Log( '%sWebSocket %s from %s:%s.'
                        % ( ('SSL-' if request.IsSSL else ''),
                            'accepted' if onWSAccepted else 'denied',
                            self._xasCli.CliAddr[0],
                            self._xasCli.CliAddr[1] ),
                        self._mws2.INFO )

        if not onWSAccepted :
            self._close(1001, 'Going away...')
            return

        self._xasCli.OnClosed = self._onXAsCliClosed

        try :
            onWSAccepted(self._mws2, self)
        except Exception as ex :
            self._mws2.Log( 'Exception raised from "WebSockets.OnWebSocketAccepted" handler: %s' % ex,
                            self._mws2.ERROR )
            self._close(1011, 'Unexpected error')
            return

        self._waitFrame()

    # ------------------------------------------------------------------------

    def _recvData(self, onRecv, size=None) :
        self._xasCli.AsyncRecvData( size       = size,
                                    onDataRecv = onRecv,
                                    timeoutSec = self._mws2.RequestsTimeoutSec )

    # ------------------------------------------------------------------------

    def _onXAsCliClosed(self, xasCli, closedReason) :
        self._isClosed = True
        if self._onClosed :
            try :
                self._onClosed(self)
            except Exception as ex :
                self._mws2.Log( 'Exception raised from "WebSocket.OnClosed" handler: %s' % ex,
                                self._mws2.ERROR )

    # ------------------------------------------------------------------------

    def _waitFrame(self) :
        
        def onHdrStartingRecv(xasCli, data, arg) :

            fin    = data[0] & 0x80 > 0
            opcode = data[0] & 0x0F
            masked = data[1] & 0x80 > 0
            length = data[1] & 0x7F

            # Control frame ?
            isCtrlFrame = ( opcode != WebSocket._OP_FRAME_TEXT and \
                            opcode != WebSocket._OP_FRAME_BIN  and \
                            opcode != WebSocket._OP_FRAME_CONT )

            if ( isCtrlFrame and not fin ) \
               or \
               ( opcode == WebSocket._OP_FRAME_CONT and \
                 not self._currentMsgType ) \
               or \
               ( self._currentMsgType and \
                 ( opcode == WebSocket._OP_FRAME_TEXT or \
                   opcode == WebSocket._OP_FRAME_BIN ) ) :
                # Bad frame in the context,
                self._close(1002, 'Protocol error (bad frame in the context)')
                return

            def endOfHeader(dataLen, maskingKey) :

                def onPayloadDataRecv(xasCli, data, arg) :

                    if maskingKey :
                        for i in range(dataLen) :
                            data[i] ^= maskingKey[i%4]
                    
                    if self._currentMsgData :
                        try :
                            self._currentMsgData += data
                        except :
                            # Frame is too large for memory allocation,
                            self._close(1009, 'Frame is too large to be processed')
                            return
                    else :
                        self._currentMsgData = data

                    if fin :
                        # Frame is fully received,
                        if self._currentMsgType == WebSocket._MSG_TYPE_TEXT :
                            # Text frame,
                            if self._onTextMsg :
                                try :
                                    msg = bytes(self._currentMsgData).decode('UTF-8')
                                    try :
                                        self._onTextMsg(self, msg)
                                    except Exception as ex :
                                        self._mws2.Log( 'Exception raised from "WebSocket.OnTextMessage" handler: %s' % ex,
                                                        self._mws2.ERROR )
                                        self._close(1011, 'Unexpected error while processing text message')
                                        return
                                except :
                                    self._mws2.Log( 'Error during UTF-8 decoding of websocket text message.',
                                                    self._mws2.WARNING )
                                    self._close(1007, 'Error to decode UTF-8 text message')
                                    return
                            else :
                                self._close(1003, 'Text messages are not implemented')
                                return
                        elif self._currentMsgType == WebSocket._MSG_TYPE_BIN :
                            # Binary frame,
                            if self._onBinMsg :
                                try :
                                    self._onBinMsg(self, bytes(self._currentMsgData))
                                except Exception as ex :
                                    self._mws2.Log( 'Exception raised from "WebSocket.OnBinaryMessage" handler: %s' % ex,
                                                    self._mws2.ERROR )
                                    self._close(1011, 'Unexpected error while processing binary message')
                                    return
                            else :
                                self._close(1003, 'Binary messages are not implemented')
                                return

                        self._currentMsgType = None
                        self._currentMsgData = None
                    
                    self._waitFrame()
                    
                    # - End of onPayloadDataRecv -

                if not isCtrlFrame :
                    # Message frame or continuation frame,
                    if self._maxRecvMsgLen :
                        l = dataLen
                        if self._currentMsgData :
                            l += len(self._currentMsgData)
                        if l > self._maxRecvMsgLen :
                            # Message length exceeds the defined limit,
                            self._close(1009, 'Frame is too large to be processed')
                            return
                    if opcode == WebSocket._OP_FRAME_TEXT :
                        self._currentMsgType = WebSocket._MSG_TYPE_TEXT
                    elif opcode == WebSocket._OP_FRAME_BIN :
                        self._currentMsgType = WebSocket._MSG_TYPE_BIN
                    try :
                        self._recvData(onPayloadDataRecv, dataLen)
                    except :
                        # Frame is too large for memory allocation,
                        self._close(1009, 'Frame is too large to be processed')
                elif opcode == WebSocket._OP_FRAME_PING :
                    # Ping control frame,
                    if dataLen > 0 :
                        def onPingDataRecv(xasCli, data, arg) :
                            data = bytearray(data)
                            self._sendFrame(WebSocket._OP_FRAME_PONG, data)
                            self._waitFrame()
                        self._recvData(onPingDataRecv, dataLen)
                    else :
                        self._sendFrame(WebSocket._OP_FRAME_PONG)
                        self._waitFrame()
                elif opcode == WebSocket._OP_FRAME_PONG :
                    # Pong control frame,
                    if dataLen > 0 :
                        def onPongDataRecv(xasCli, data, arg) :
                            self._waitFrame()
                        self._recvData(onPongDataRecv, dataLen)
                    else :
                        self._waitFrame()
                elif opcode == WebSocket._OP_FRAME_CLOSE :
                    # Close control frame,')
                    if dataLen > 0 :
                        def onCloseDataRecv(xasCli, data, arg) :
                            self._close()
                        self._recvData(onCloseDataRecv, dataLen)
                    else :
                        self._close()
                else :
                    # Unknown frame type,
                    self._close(1002, 'Protocol error (bad opcode)')

                # - End of endOfHeader -

            def getMaskingKey(dataLen) :
                
                if masked :
                    # Frame is masked by the next 4 bytes key,
                    def onMaskingKeyRecv(xasCli, data, arg) :
                        endOfHeader(dataLen=dataLen, maskingKey=bytes(data))
                    self._recvData(onMaskingKeyRecv, 4)
                else :
                    # Frame is not masked,
                    endOfHeader(dataLen=dataLen, maskingKey=None)

                # - End of getMaskingKey -

            if length == 0 and not isCtrlFrame :
                # Bad frame for a no control frame without payload data,
                self._close(1002, 'Protocol error (payload data required)')
            elif length <= 0x7D :
                # Frame length <= 0x7D,
                getMaskingKey(dataLen=length)
            elif isCtrlFrame :
                # Bad frame for length of control frame > 0x7D,
                self._close(1002, 'Protocol error (bad control frame length)')
            elif length == 0x7E :
                # Frame length is encoded on next 16 bits,
                def onLenExt1Recv(xasCli, data, arg) :
                    length = (data[0] << 8) + data[1]
                    if length < 0x7E :
                        # Bad frame for 16 bits length < 0x7E,
                        self._close(1002, 'Protocol error (bad length encoding)')
                    else :
                        getMaskingKey(dataLen=length)
                self._recvData(onLenExt1Recv, 2)
            else :
                # Frame length is encoded on next 64 bits.
                # It's too large and not implemented,
                self._close(1009, 'Frame is too large to be processed')

            # - End of onHdrStartingRecv -

        self._xasCli.AsyncRecvData( size       = 2,
                                    onDataRecv = onHdrStartingRecv,
                                    timeoutSec = self._waitFrameTimeoutSec )

    # ------------------------------------------------------------------------

    def _sendFrame(self, opcode, data=None, fin=True) :
        try :
            if opcode >= 0x00 and opcode <= 0x0F :
                length = len(data) if data else 0
                if length <= 0xFFFF :
                    data = bytes([ (opcode | 0x80) if fin else opcode ] )  \
                         + bytes([ length if length <= 0x7D else 0x7E ] )  \
                         + (pack('>H', length) if length >= 0x7E else b'') \
                         + (bytes(data) if data else b'')
                    return self._xasCli.AsyncSendData(data)
        except :
            pass
        return False

    # ------------------------------------------------------------------------

    def _close(self, statusCode=None, reason=None, waitCloseFrame=False) :
        if not self._isClosed :
            if statusCode :
                data = pack('>H', statusCode)
                if reason :
                    data += reason.encode('UTF-8')
            else :
                data = None
            self._sendFrame(WebSocket._OP_FRAME_CLOSE, data)
            self._isClosed = True
            if waitCloseFrame :
                return
        self._xasCli.Close()

    # ------------------------------------------------------------------------

    def SendTextMessage(self, msg) :
        if not isinstance(msg, str) or len(msg) == 0 :
            raise ValueError('"msg" must be a not empty string.')
        if not self._isClosed :
            try :
                msg = msg.encode('UTF-8')
            except :
                return False
            return self._sendFrame(WebSocket._OP_FRAME_TEXT, msg)
        return False

    # ------------------------------------------------------------------------

    def SendBinaryMessage(self, msg) :
        try :
            bytes([msg[0]])
        except :
            raise ValueError('"msg" must be a not empty bytes object.')
        if not self._isClosed :
            return self._sendFrame(WebSocket._OP_FRAME_BIN, msg)
        return False

    # ------------------------------------------------------------------------

    def Close(self) :
        if not self._isClosed :
            self._close(1000, 'Normal closure', waitCloseFrame=True)

    # ------------------------------------------------------------------------

    @property
    def Request(self) :
        return self._request

    # ------------------------------------------------------------------------

    @property
    def IsClosed(self) :
        return self._isClosed

    # ------------------------------------------------------------------------

    @property
    def WaitFrameTimeoutSec(self) :
        return self._waitFrameTimeoutSec

    @WaitFrameTimeoutSec.setter
    def WaitFrameTimeoutSec(self, value) :
        if not isinstance(value, int) or value <= 0 :
            raise ValueError('"WaitFrameTimeoutSec" must be a positive integer.')
        self._waitFrameTimeoutSec = value

    # ------------------------------------------------------------------------

    @property
    def MaxRecvMessageLength(self) :
        return self._maxRecvMsgLen

    @MaxRecvMessageLength.setter
    def MaxRecvMessageLength(self, value) :
        if value is not None and (not isinstance(value, int) or value < 125) :
            raise ValueError('"MaxRecvMessageLength" must be an integer >= 125 or None.')
        self._maxRecvMsgLen = value

    # ------------------------------------------------------------------------

    @property
    def OnTextMessage(self) :
        return self._onTextMsg

    @OnTextMessage.setter
    def OnTextMessage(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnTextMessage" must be a function.')
        self._onTextMsg = value

    # ------------------------------------------------------------------------

    @property
    def OnBinaryMessage(self) :
        return self._onBinMsg

    @OnBinaryMessage.setter
    def OnBinaryMessage(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnBinaryMessage" must be a function.')
        self._onBinMsg = value

    # ------------------------------------------------------------------------

    @property
    def OnClosed(self) :
        return self._onClosed

    @OnClosed.setter
    def OnClosed(self, value) :
        if type(value) is not type(lambda x:x) :
            raise ValueError('"OnClosed" must be a function.')
        self._onClosed = value

# ============================================================================
# ============================================================================
# ============================================================================
