import google.oauth2.credentials

from pickle import load 
from pickle import dump
from os import path
from time import sleep
from re import compile as comp

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QLabel

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from oauth2client import tools
from oauth2client.file import Storage
from oauth2client import client

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    credentials = None
    if path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
 
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            dump(credentials, token)
 
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
    
def get_video_comments(service, **kwargs):
    comments = []
    results = service.commentThreads().list(**kwargs).execute()

    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if 'replies' in item.keys():
                for reply in item['replies']['comments']:
                    comments.append(reply)

        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.commentThreads().list(**kwargs).execute()
        else:
            break

    return comments

class LoadingScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(42,42)
        self.setWindowOpacity(0.4)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        
        self.label_animation = QtWidgets.QLabel(self)
        
        self.movie = QtGui.QMovie("loading.gif", QtCore.QByteArray(), self)
        #self.movie.setBackgroundColor(Qt.transparent)
        #self.movie.setScaledSize(QtCore.QSize().scaled(40, 40, Qt.KeepAspectRatio))
        self.label_animation.setMovie(self.movie)
        
        self.movie.start()
        
        self.setVisible(True)
    
    def stopAnimation(self):
        self.movie.stop()
        self.close()

        
class Ui_frame(object):
    def setupUi(self, frame):
        frame.setObjectName("frame")
        frame.resize(640, 480)
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.formLayout = QtWidgets.QFormLayout(frame)
        self.formLayout.setObjectName("formLayout")
        
        self.linkLabel = QtWidgets.QLabel(frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.linkLabel.setFont(font)
        self.linkLabel.setObjectName("linkLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.linkLabel)
        
        self.lineEdit = QtWidgets.QLineEdit(frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.lineEdit)
        
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.hash2 = QtWidgets.QLabel(frame)
        
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.hash2.setFont(font)
        self.hash2.setObjectName("hash2")
        self.gridLayout.addWidget(self.hash2, 0, 1, 1, 1)
        self.hashtag1In = QtWidgets.QLineEdit(frame)
        
        font = QtGui.QFont()
        font.setPointSize(10)
        self.hashtag1In.setFont(font)
        self.hashtag1In.setObjectName("hashtag1In")
        self.gridLayout.addWidget(self.hashtag1In, 1, 0, 1, 1)
        self.hash1 = QtWidgets.QLabel(frame)
        self.hash1.setEnabled(True)
        
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.hash1.setFont(font)
        self.hash1.setObjectName("hash1")
        self.gridLayout.addWidget(self.hash1, 0, 0, 1, 1)
        self.hashtag2In = QtWidgets.QLineEdit(frame)
        
        font = QtGui.QFont()
        font.setPointSize(10)
        self.hashtag2In.setFont(font)
        self.hashtag2In.setObjectName("hashtag2In")
        self.gridLayout.addWidget(self.hashtag2In, 1, 1, 1, 1)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.SpanningRole, self.gridLayout)
        self.outputBox = QtWidgets.QTextBrowser(frame)
        
        font = QtGui.QFont()
        font.setPointSize(10)
        self.outputBox.setFont(font)
        self.outputBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.outputBox.setObjectName("outputBox")
        
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.outputBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.SpanningRole, spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(6, QtWidgets.QFormLayout.SpanningRole, spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.SpanningRole, spacerItem2)
        
        self.pushButton = QtWidgets.QPushButton(frame)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.pushButton)

        self.retranslateUi(frame)
        QtCore.QMetaObject.connectSlotsByName(frame)

    def retranslateUi(self, frame):
        _translate = QtCore.QCoreApplication.translate
        frame.setWindowIcon(QtGui.QIcon('icon.png'))
        frame.setWindowTitle(_translate("frame", "YouTube Hashtag Counter 1.1"))
        self.linkLabel.setText(_translate("frame", "YouTube URL to Video:"))
        self.hash2.setText(_translate("frame", "Keyword 2:"))
        self.hash1.setText(_translate("frame", "Keyword 1:"))
        self.pushButton.setText(_translate("frame", "Count votes"))
        self.pushButton.clicked.connect(lambda: self.runCounter(frame))
        
    def runCounter(self, frame):
        self.pushButton.setEnabled(False)
        self.thread = CalcThread(self)
        self.thread.start()
        
class  CalcThread(QThread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        
        global loading
        loading = LoadingScreen()
        
    def run(self):
        skip = False
        
        try:
            url = str(self.ui.lineEdit.text())
            regex = comp(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')

            match = regex.match(url)
            videoid = match.group('id')
        except:
            self.ui.outputBox.append("Video URL missing or incorrect.\n")
            skip = True
        
        if not skip:
            try:
                coms = get_video_comments(service, videoId=videoid, part='id,snippet,replies')
            except:
                self.ui.outputBox.append("Could not find video or connection refused. Check your internet connection or video URL.\n")
                skip = True
        
        if not skip:
            print("wf?")
            name1 = str(self.ui.hashtag1In.text()).lower()
            name2 = str(self.ui.hashtag2In.text()).lower()
        
            hashtag1 = 0
            hashtag2 = 0
        
            if name1 == "":
                hashtag1 = -1
            if name2 == "":
                hashtag2 = -1
        
            for com in coms:   
                if name1 in str(com).lower() and hashtag1 != -1:
                    hashtag1 += 1
                if name2 in str(com).lower() and hashtag2 != -1:
                    hashtag2 += 1
                
            if hashtag1 != -1:
                try:
                    percent1 = hashtag1 / (hashtag1 + hashtag2) * 100
                except:
                    percent1 = 0
            else:
                percent1 = 0
                hashtag1 = 0
                name1 = "NONE"
        
            if hashtag2 != -1:
                try:
                    percent2 = hashtag2 / (hashtag1 + hashtag2) * 100
                except:
                    percent2 = 0
            else:
                percent2 = 0
                hashtag2 = 0
                name2 = "NONE"
        
            loading.stopAnimation()
        
            percent1 = "{:.2f}".format(percent1)
            percent2 = "{:.2f}".format(percent2)
        
        
            self.ui.outputBox.append(name1 + ": " + str(hashtag1) + " (" + str(percent1) + "%)" + "\n" + name2 + 
                                  ": " + str(hashtag2) + " (" + str(percent2) + "%)" + "\n")
            
        sleep(1)
        loading.stopAnimation()
        self.ui.pushButton.setEnabled(True)
        self.quit()
    
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = QtWidgets.QFrame()
    ui = Ui_frame()
    ui.setupUi(frame)
    
    try:
        service = get_authenticated_service()
    except:
        ui.outputBox.append("Failed to load a valid user session or connect to google services. Make sure you have a valid client_secret.json file and check your internet connection then restart the application.")
        ui.pushButton.setEnabled(False)
    
    frame.show()
    sys.exit(app.exec_())