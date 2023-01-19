import praw
import base64
import hashlib
import webbrowser
import re
import os
# from scroller.ResponseServer import ResponseServer
from PySide6.QtCore import Signal, Slot, QObject
from PySide6.QtNetwork import QHostAddress

CLIENT_ID = 'WiziQHdS_6gEygt0PVJhoA'
REDIRECT_URI = 'http://localhost:8091/callback'
USER_AGENT = 'scroller/0.2.1 (by /u/draugexa)'

class RedditOAuth2(QObject):
    authenticated = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=None,
            redirect_uri=REDIRECT_URI,
            user_agent=USER_AGENT
        )
        
        self.isAuthenticated = False
        # self.verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
        # self.verifier = re.sub('[^a-zA-Z0-9]+', '', self.verifier)
        # self.challenge = hashlib.sha256(self.verifier.encode('utf-8')).digest()
        # self.challenge = base64.urlsafe_b64encode(self.challenge).decode('utf-8')
        # self.challenge = self.challenge.replace('=', '')
        # self.uniqueState = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
        # self.uniqueState = re.sub('[^a-zA-Z0-9]+', '', self.verifier)
        # self.listener = ResponseServer(self.uniqueState)
        # self.listener.verificationReceived.connect(lambda params: self.onVerificationReceived(params['code']))
        # self.authenticated.connect(self.onAuthenticated)

        self.onAuthenticated(True)

    def beginAuthentication(self):
        """
        Opens a web view to authenticate the user with Reddit.
        """
        url = self.reddit.auth.url(
            scopes=["*"],
            state=self.uniqueState,
            duration="permanent"
        )
        self.listener.listen(QHostAddress.LocalHost, 8091)
        webbrowser.open(url)

    @Slot(str)
    def onVerificationReceived(self, code: str):
        """
        Requests an access token from Reddit's OAuth2 API
        """
        try:
            self.reddit.auth.authorize(code)
            self.authenticated.emit(True)
        except:
            self.authenticated.emit(False)
    
    @Slot(bool)
    def onAuthenticated(self, success: bool):
        """
        Called when the user has been authenticated.
        """
        self.isAuthenticated = success
    
    