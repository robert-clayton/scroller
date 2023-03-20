import praw
import os
import requests
from scroller.Models.ImageModel import ImageModel
from PySide6.QtCore import QModelIndex, Slot


CLIENT_ID = 'WiziQHdS_6gEygt0PVJhoA'
REDIRECT_URI = 'http://localhost:8091/callback'
USER_AGENT = 'scroller/0.2.1 (by /u/draugexa)'


class ImageModelReddit(ImageModel):
    # authenticated = Signal(bool)

    def __init__(self):
        super().__init__()
        self.reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=None,
            redirect_uri=REDIRECT_URI,
            user_agent=USER_AGENT
        )
        self.count = 0

        # create tmp folder for storing images
        self.tmpFolder = os.path.join(os.path.expanduser('~'), '.scroller', 'tmp')
        if not os.path.exists(self.tmpFolder):
            os.makedirs(self.tmpFolder)
        
        self.oldPosts = []
        self.maxReached = False

    def setFolder(self, folder: str):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.imageData = []
        self.endRemoveRows()

        self.imageList = self.reddit.subreddit(str(folder)).new(limit=None)
        for post in self.imageList:
            if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                self.toGenerateList.append(post.url)
                self.count +=1
                print(self.count)
            if len(self.toGenerateList) == 60:
                break

        self.threadPool.cancelAll()

        # clear tmp folder
        for file in os.listdir(self.tmpFolder):
            os.remove(os.path.join(self.tmpFolder, file))

        for proxy in self.proxies.values():
            self.generateImages(count=10, proxyID=proxy.getProxyID())
    
    @Slot(list, int, result=list)
    def generateImageData(self, generationList: list, proxyID: int) -> list[dict]:
        """
        Generate image data for the given list of remote image paths
        """
        folderGenerationList = []
        for url in generationList:
            # check if url or path, aka 'already downloaded'
            if not url.startswith('http'):
                folderGenerationList.append(url)
                continue

            # download url to tmp folder
            filename = os.path.join(self.tmpFolder, url.split('/')[-1])
            response = requests.get(url)
            if response.status_code != 200:
                continue
            with open(filename, 'wb') as f:
                f.write(response.content)
            folderGenerationList.append(filename)
        return super().generateImageData(folderGenerationList, proxyID)
    
    def generateImages(self, count: int = 1, proxyID: int = 0):
        targetCount = len(self.toGenerateList) + count
        if not self.maxReached:
            for post in self.imageList:
                if post.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    self.toGenerateList.append(post.url)
                if len(self.toGenerateList) == targetCount:
                    break
            if len(self.toGenerateList) != targetCount: 
                self.maxReached = True
        else:
            self.imageList = self.oldPosts

        super().generateImages(count, proxyID)

    #     self.isAuthenticated = False
    #     self.verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    #     self.verifier = re.sub('[^a-zA-Z0-9]+', '', self.verifier)
    #     self.challenge = hashlib.sha256(self.verifier.encode('utf-8')).digest()
    #     self.challenge = base64.urlsafe_b64encode(self.challenge).decode('utf-8')
    #     self.challenge = self.challenge.replace('=', '')
    #     self.uniqueState = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    #     self.uniqueState = re.sub('[^a-zA-Z0-9]+', '', self.verifier)
    #     self.listener = ResponseServer(self.uniqueState)
    #     self.listener.verificationReceived.connect(lambda params: self.onVerificationReceived(params['code']))
    #     self.authenticated.connect(self.onAuthenticated)

    #     self.onAuthenticated(True)

    # def beginAuthentication(self):
    #     """
    #     Opens a web view to authenticate the user with Reddit.
    #     """
    #     url = self.reddit.auth.url(
    #         scopes=["*"],
    #         state=self.uniqueState,
    #         duration="permanent"
    #     )
    #     self.listener.listen(QHostAddress.LocalHost, 8091)
    #     webbrowser.open(url)

    # @Slot(str)
    # def onVerificationReceived(self, code: str):
    #     """
    #     Requests an access token from Reddit's OAuth2 API
    #     """
    #     try:
    #         self.reddit.auth.authorize(code)
    #         self.authenticated.emit(True)
    #     except:
    #         self.authenticated.emit(False)
    
    # @Slot(bool)
    # def onAuthenticated(self, success: bool):
    #     """
    #     Called when the user has been authenticated.
    #     """
    #     self.isAuthenticated = success
