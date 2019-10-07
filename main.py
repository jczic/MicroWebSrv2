

from MicroWebSrv2  import *
from XAsyncSockets import XAsyncSocketsPool
from time          import sleep
from _thread       import allocate_lock

# ============================================================================
# ============================================================================
# ============================================================================

@WebRoute(GET, '/test-redir')
def RequestTestRedirect(microWebSrv2, request) :
    request.Response.ReturnRedirect('/test.pdf')

# ============================================================================
# ============================================================================
# ============================================================================

@WebRoute(GET, '/test-post', name='TestPost1/2')
def RequestTestPost(microWebSrv2, request) :
    content = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>POST 1/2</title>
        </head>
        <body>
            <h2>MicroWebSrv2 - POST 1/2</h2>
            User address: %s<br />
            <form action="/test-post" method="post">
                First name: <input type="text" name="firstname"><br />
                Last name:  <input type="text" name="lastname"><br />
                <input type="submit" value="OK">
            </form>
        </body>
    </html>
    """ % request.UserAddress[0]
    request.Response.ReturnOk(content)

# ------------------------------------------------------------------------

@WebRoute(POST, '/test-post', name='TestPost2/2')
def RequestTestPost(microWebSrv2, request) :
    formData  = request.GetPostedFormData()
    try :
        firstname = formData['firstname']
        lastname  = formData['lastname']
    except :
        request.Response.ReturnBadRequest()
        return
    content   = """\
    <!DOCTYPE html>
    <html>
        <head>
            <title>POST 2/2</title>
        </head>
        <body>
            <h2>MicroWebSrv2 - POST 2/2</h2>
            Hello %s %s :)<br />
        </body>
    </html>
    """ % ( MicroWebSrv2.HTMLEscape(firstname),
            MicroWebSrv2.HTMLEscape(lastname) )
    request.Response.ReturnOk(content)

# ============================================================================
# ============================================================================
# ============================================================================

def OnWebSocketAccepted(microWebSrv2, webSocket) :
    print('Example WebSocket accepted:')
    print('   - User   : %s:%s' % webSocket.Request.UserAddress)
    print('   - Path   : %s'    % webSocket.Request.Path)
    print('   - Origin : %s'    % webSocket.Request.Origin)
    if webSocket.Request.Path.lower() == '/wschat' :
        WSJoinChat(webSocket)
    else :
        webSocket.OnTextMessage   = OnWebSocketTextMsg
        webSocket.OnBinaryMessage = OnWebSocketBinaryMsg
        webSocket.OnClosed        = OnWebSocketClosed

# ============================================================================
# ============================================================================
# ============================================================================

def OnWebSocketTextMsg(webSocket, msg) :
    print('WebSocket text message: %s' % msg)
    webSocket.SendTextMessage('Received "%s"' % msg)

# ------------------------------------------------------------------------

def OnWebSocketBinaryMsg(webSocket, msg) :
    print('WebSocket binary message: %s' % msg)

# ------------------------------------------------------------------------

def OnWebSocketClosed(webSocket) :
    print('WebSocket %s:%s closed' % webSocket.Request.UserAddress)

# ============================================================================
# ============================================================================
# ============================================================================

global _chatWebSockets
_chatWebSockets = [ ]

global _chatLock
_chatLock = allocate_lock()

# ------------------------------------------------------------------------

def WSJoinChat(webSocket) :
    webSocket.OnTextMessage = OnWSChatTextMsg
    webSocket.OnClosed      = OnWSChatClosed
    with _chatLock :
        for ws in _chatWebSockets :
            wsIP = ws.Request.UserAddress[0]
            ws.SendTextMessage('<%s has joined the chat>' % wsIP)
        _chatWebSockets.append(webSocket)

# ------------------------------------------------------------------------

def OnWSChatTextMsg(webSocket, msg) :
    with _chatLock :
        for ws in _chatWebSockets :
            wsIP = ws.Request.UserAddress[0]
            ws.SendTextMessage('<%s> %s' % (wsIP, msg))

# ------------------------------------------------------------------------

def OnWSChatClosed(webSocket) :
    with _chatLock :
        if webSocket in _chatWebSockets :
            _chatWebSockets.remove(webSocket)
        for ws in _chatWebSockets :
            wsIP = ws.Request.UserAddress[0]
            ws.SendTextMessage('<%s left the chat>' % wsIP)

# ============================================================================
# ============================================================================
# ============================================================================

wsMod = MicroWebSrv2.LoadModule('WebSockets')
wsMod.OnWebSocketAccepted = OnWebSocketAccepted

print()

xasPool = XAsyncSocketsPool()
mws2    = MicroWebSrv2()

mws2.EnableSSL( certFile = 'openhc2.crt',
                keyFile  = 'openhc2.key' )
mws2.NotFoundURL = '/'

print('Starts MicroWebSrv2')
mws2.Start(xasPool)

print('Starts pool processing')
xasPool.AsyncWaitEvents(threadsCount=1)

try :
    while True :
        sleep(60)
except KeyboardInterrupt :
    print()
    print('Stops MicroWebSrv2')
    mws2.Stop()
    print('Terminates pool processing...')
    xasPool.StopWaitEvents()
    print('Bye')
    print()

# ============================================================================
# ============================================================================
# ============================================================================
