import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QLineEdit


class c_tupZilla(QMainWindow):
    def __init__(self):
        super(c_tupZilla, self).__init__()
        self.str_urlHome = 'http://google.com'
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.str_urlHome))
        self.setCentralWidget(self.browser)
        self.init_navBar()
        self.init_searchBar()
        self.showMaximized()
        
    def init_navBar(self):
        navBar = QToolBar()
        self.addToolBar(navBar)
        d_buton = {'Back': self.browser.back, 
                   'Forward': self.browser.forward,
                   'Reload': self.browser.reload,
                   'Home': self.navigate_home}
        for n, action in d_buton.items():
            btn = QAction(n, self)
            btn.triggered.connect(action)
            navBar.addAction(btn)
        self.navBar = navBar
    
    def init_searchBar(self):
        url_bar = QLineEdit()
        url_bar.returnPressed.connect(self.navigate_to_url)
        self.navBar.addWidget(url_bar)
        # Update Search Bar when moving around
        self.browser.urlChanged.connect(self.update_url)
        self.url_bar = url_bar
        
    def navigate_home(self):
        self.browser.setUrl(QUrl(self.str_urlHome))
        
    def navigate_to_url(self):
        str_url = self.url_bar.text()
        self.browser.setUrl(QUrl(str_url))
        
    def update_url(self, q_param):
        self.url_bar.setText(q_param.toString())
        
        
        
if __name__ == '__main__':
    if not QApplication.instance(): app = QApplication(sys.argv)
    else:                           app = QApplication.instance()
    
    QApplication.setApplicationName('Tup-Zilla')
    
    widget = c_tupZilla()
    widget.show()

    if not QApplication.instance(): app = sys.exit(app.exec_())
    else:                           app = app.exec_()


