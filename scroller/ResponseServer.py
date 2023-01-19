from PySide6.QtCore import QByteArray, QTimer, Signal, QUrl, QUrlQuery
from PySide6.QtNetwork import QTcpServer

class ResponseServer(QTcpServer):
    verificationReceived = Signal(object)
    serverClosed = Signal(object)

    def __init__(self, uniqueState: str):
        super().__init__()
        self.timeout = 15000
        self.maxTries = 3
        self.tries = 0
        self.replyContent = b"""
        <html>
            <head>
                <title>Authentication Successful</title>
            </head>
            <body>
                <h1>Thank you for authenticating!</h1>
                <p>You may now close this window.</p>
            </body>
        </html>
        """
        
        self.uniqueState = uniqueState
        self.newConnection.connect(self.onIncomingConnection)

    def onIncomingConnection(self):
        socket = self.nextPendingConnection()
        socket.readyRead.connect(self.onBytesReady)
        socket.disconnected.connect(socket.deleteLater)

        # wait for usable data before timeout
        timer = QTimer(socket)
        timer.setObjectName('timeoutTimer')
        timer.setSingleShot(True)
        timer.setInterval(self.timeout)
        timer.timeout.connect(self.closeServer)
        socket.readyRead.connect(timer.start)

    def onBytesReady(self):
        if not self.isListening():
            return
        socket = self.sender()
        if not socket:
            return
        reply = QByteArray()
        reply.append(b"HTTP/1.0 200 OK \r\n")
        reply.append(b"Content-Type: text/html; charset=\"utf-8\"\r\n")
        reply.append(b"Content-Length: %d\r\n\r\n" % len(self.replyContent))
        reply.append(self.replyContent)
        socket.write(reply)

        data = socket.readAll()
        queryParams = self.parseQueryParams(data)
        if not len(queryParams):
            if self.tries < self.maxTries:
                self.tries += 1
                return
            self.tries = 0
            self.closeServer(socket, False)
            return
        if self.uniqueState != queryParams['state']:
            self.closeServer(socket, True)
            return
        self.closeServer(socket, True)
        self.verificationReceived.emit(queryParams)

    def parseQueryParams(self, data):
        splitGetLine = str(data, 'utf-8').split('\r\n')[0]
        splitGetLine = splitGetLine.replace('GET ', '').replace('HTTP/1.1', '').replace('\\r\\n', '')
        splitGetLine = 'http://localhost:{}{}'.format(self.serverPort(), splitGetLine)

        tokens = QUrlQuery(QUrl(splitGetLine)).queryItems()
        queryParams = {}
        for tokenPair in tokens:
            key = QUrl.fromPercentEncoding(tokenPair[0].strip().encode('utf-8'))
            value = QUrl.fromPercentEncoding(tokenPair[1].strip().encode('utf-8'))
            queryParams[key] = value
        return queryParams

    def closeServer(self, socket=None, hasParameters=False):
        if not self.isListening():
            return
        if not socket and self.sender():
            if isinstance(self.sender(), QTimer):
                print('ResponseServer::closeServer: Closing due to timeout')
                self.sender().stop()
                socket = self.sender().parent()
                self.sender().deleteLater()
        if socket:
            timer = socket.findChild(QTimer, "timeoutTimer")
            if timer:
                timer.stop()
            socket.disconnectFromHost()
        
        self.close()
        self.serverClosed.emit(hasParameters)