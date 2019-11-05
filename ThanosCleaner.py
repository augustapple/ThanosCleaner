from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from packaging import version
import os
import re
import sys
import time
import js2py
import ctypes
import requests
import threading
import logging
import logging.handlers
from bs4 import BeautifulSoup

loginFlag = False
exitFlag = False
deleteFlag = False
VERSION = "1.61"
UPDATE_URL = "https://github.com/augustapple/ThanosCleaner/raw/master/version.json"

decode_service_code='''
    function get_service_code(service_code, r_value){
    var a,e,n,t,f,d,h,i = "yL/M=zNa0bcPQdReSfTgUhViWjXkYIZmnpo+qArOBs1Ct2D3uE4Fv5G6wHl78xJ9K",
    o = "",
    c = 0;
    for (r_value = r_value.replace(/[^A-Za-z0-9+/=]/g,""); c < r_value.length;) {
        t = i.indexOf(r_value.charAt(c++));
        f = i.indexOf(r_value.charAt(c++));
        d = i.indexOf(r_value.charAt(c++));
        h = i.indexOf(r_value.charAt(c++));
        a = t << 2 | f >> 4;
        e = (15 & f) << 4 | d >> 2;
        n = (3 & d) << 6 | h;
        o += String.fromCharCode(a);
        64 != d && (o += String.fromCharCode(e));
        64 != h && (o += String.fromCharCode(n));
        }
        var tvl = o;
        var fi = parseInt(tvl.substr(0,1));
        fi = fi > 5 ? fi - 5 : fi + 4;
        var _r = tvl.replace(/^./, fi);
        var _rs = _r.split(",");
        var replace = "";
        for (e = 0; e < _rs.length; e++) replace += String.fromCharCode(2 * (_rs[e] - e - 1) / (13 - e - 1));
        return service_code.replace(/(.{10})$/, replace)
    }
    '''
decode_service_code = js2py.eval_js(decode_service_code)

class MyWidget(QWidget):
	def __init__(self):
		super().__init__()
		rootLogger.debug("Application started")

		layout = QGridLayout()

		self.lbl_id = QLabel("ID : ", self)
		self.qle_id = QLineEdit(self)
		self.qle_id.returnPressed.connect(self.tryLogin)
		self.lbl_pw = QLabel("PW : ", self)
		self.qle_pw = QLineEdit(self)
		self.qle_pw.returnPressed.connect(self.tryLogin)
		self.cbx_pw = QCheckBox("숨김", self)
		self.cbx_pw.stateChanged.connect(self.hidePassword)
		self.cbx_pw.toggle()
		self.btn_login = QPushButton("로그인", self)
		self.btn_login.clicked.connect(self.tryLogin)
		self.btn_login.setStatusTip("로그인하기")
		self.btn_logout = QPushButton("로그아웃", self)
		self.btn_logout.setEnabled(False)
		self.btn_logout.clicked.connect(self.logout)
		self.btn_logout.setStatusTip("로그아웃하기")
		self.status = "로그인되지 않음"
		self.lbl_status = QLabel("로그인 상태 : %s" % self.status, self)
		self.lbl_post = QLabel("게시글 수 : 알 수 없음")
		self.lbl_comment = QLabel("댓글 수 : 알 수 없음")
		self.lbl_scrap = QLabel("스크랩 수 : 알 수 없음")
		self.lbl_guestbook = QLabel("방명록 수 : 알 수 없음")
		self.btn_delPost = QPushButton("게시글 삭제", self)
		self.btn_delPost.clicked.connect(self.tryDelPost)
		self.btn_delPost.setStatusTip("모든 게시글 삭제")
		self.btn_delComment = QPushButton("댓글 삭제", self)
		self.btn_delComment.clicked.connect(self.tryDelComment)
		self.btn_delComment.setStatusTip("모든 댓글 삭제")
		self.btn_delScrap = QPushButton("스크랩 삭제", self)
		self.btn_delScrap.clicked.connect(self.tryDelScrap)
		self.btn_delScrap.setStatusTip("모든 스크랩 삭제")
		self.btn_delGuestbook = QPushButton("방명록 삭제", self)
		self.btn_delGuestbook.clicked.connect(self.tryDelGuestbook)
		self.btn_delGuestbook.setStatusTip("모든 방명록 삭제")
		self.btn_cancelDelProcess = QPushButton("삭제 중단", self)
		self.btn_cancelDelProcess.setEnabled(False)
		self.btn_cancelDelProcess.clicked.connect(self.cancelDelProcess)
		self.btn_cancelDelProcess.setStatusTip("진행 중인 삭제 작업 중단")

		self.setLayout(layout)

		layout.addWidget(self.lbl_id, 1, 1)
		layout.addWidget(self.qle_id, 1, 2)
		layout.addWidget(self.lbl_pw, 2, 1)
		layout.addWidget(self.qle_pw, 2, 2)
		layout.addWidget(self.cbx_pw, 2, 3)
		layout.addWidget(self.btn_login, 3, 2)
		layout.addWidget(self.btn_logout, 4, 2)
		layout.addWidget(self.lbl_status, 5, 2, 1, 3)
		layout.addWidget(self.lbl_post, 6, 2)
		layout.addWidget(self.lbl_comment, 7, 2)
		layout.addWidget(self.lbl_scrap, 8, 2)
		layout.addWidget(self.lbl_guestbook, 9, 2)
		layout.addWidget(self.btn_delPost, 10, 2)
		layout.addWidget(self.btn_delComment, 11, 2)
		layout.addWidget(self.btn_delScrap, 12, 2)
		layout.addWidget(self.btn_delGuestbook, 13, 2)
		layout.addWidget(self.btn_cancelDelProcess, 14, 2)
		rootLogger.debug("Application initialized successfully")
		self.checkUpdate()

	def hidePassword(self, state):
		if state == Qt.Checked:
			self.qle_pw.setEchoMode(QLineEdit.Password)
			self.cbx_pw.setStatusTip("비밀번호 보이기")
			rootLogger.debug("Hide password is enabled")
		else:
			self.qle_pw.setEchoMode(QLineEdit.Normal)
			self.cbx_pw.setStatusTip("비밀번호 숨기기")
			rootLogger.debug("Hide password is disabled")

	def logout(self):
		global SESS, loginFlag, deleteFlag
		if deleteFlag:
			rootLogger.debug("Logout event detected while delete process")
			logoutCheck = QMessageBox.warning(self, "경고", "삭제가 진행중입니다. 로그아웃 하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
			if logoutCheck == QMessageBox.Yes:
				loginFlag = False
				SESS.close()
				self.btn_login.setEnabled(True)
				self.btn_login.setText("로그인")
				self.btn_logout.setEnabled(False)
				self.qle_id.setEnabled(True)
				self.qle_id.setText("")
				self.qle_pw.setEnabled(True)
				self.qle_pw.setText("")
				self.buttonEnable()
				rootLogger.info("Logged out")
		else:
			loginFlag = False
			SESS.close()
			self.btn_login.setEnabled(True)
			self.btn_login.setText("로그인")
			self.btn_logout.setEnabled(False)
			self.qle_id.setEnabled(True)
			self.qle_id.setText("")
			self.qle_pw.setEnabled(True)
			self.qle_pw.setText("")
			self.buttonEnable()
			deleteFlag = False
			rootLogger.info("Logged out")

	def tryLogin(self):
		self.userId = self.qle_id.text()
		self.userPw = self.qle_pw.text()

		if(self.userId == "" or self.userPw == ""):
			QMessageBox.warning(self, "경고", "아이디, 비밀번호를 입력해주세요", QMessageBox.Yes)
			rootLogger.warning("ID or password cannot be blank!")
		else:
			loginSess = self.login(self.userId, self.userPw)
			if not loginSess:
				QMessageBox.warning(self, "경고", "로그인에 실패했습니다", QMessageBox.Yes)
				rootLogger.error("Login failed")
			else:
				global loginFlag
				loginFlag = True
				self.btn_login.setEnabled(False)
				self.btn_logout.setEnabled(True)
				self.btn_login.setText("로그인 완료")
				self.qle_id.setEnabled(False)
				self.qle_pw.setEnabled(False)
				gangsinThr = (threading.Thread(target=self.gangsin, args=(SESS, self.userId)))
				gangsinThr.start()
				rootLogger.info("Logged in as %s" % self.userId)

	def login(self, userId, userPw):
		rootLogger.debug("Trying to login..")
		session = requests.session()

		global SESS
		SESS = session

		session.headers = {
			"X-Requested-With" : "XMLHttpRequest",
			"Referer" : "https://www.dcinside.com/",
			"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
		}

		soup = BeautifulSoup(session.get("https://www.dcinside.com/").text, features="lxml")
		loginForm = soup.find("form", attrs={"id" : "login_process"})
		Lauth = loginForm.find_all("input", attrs={"type" : "hidden"})[2]

		login_data = {
			"user_id" : userId,
			"pw" : userPw,
			"s_url" : "https://www.dcinside.com/",
			"ssl" : "Y",
			Lauth["name"]:Lauth["value"]
		}

		req = session.post("https://dcid.dcinside.com/join/member_check.php", data=login_data)

		session.headers = {
			"X-Requested-With" : "XMLHttpRequest",
			"Referer" : "https://gallog.dcinside.com/%s/posting" % userId,
			"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
		}

		if "history.back(-1);" in req.text:
			rootLogger.error("Cannot create login session!")
			return 0
		else:
			rootLogger.info("Login session created successfully")
			SESS = session
			return SESS

	def tryDelPost(self):
		try:
			if(loginFlag):
				rootLogger.info("Initializing post delete process..")
				self.get_service_code(self.userId, 'posting')

				self.buttonDisable()
				self.btn_delPost.setText("게시글 삭제 중..")
				self.postDelThr = (threading.Thread(target=self.delPost, args=(SESS, self.userId, service_code)))
				self.postDelThr.start()
				rootLogger.info("Post delete process started")
			else:
				rootLogger.warning("Can't delete post without login")
				QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
		except Exception as e:
			rootLogger.critical(e)
			pass

	def delPost(self, SESS, userId, service_code):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/posting" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					rootLogger.info("All posts are deleted successfully")
					self.buttonEnable()
					self.btn_delPost.setText("게시글 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[0]["data-no"]
				del content_form[0]
				deleteData = {
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(0.5)
			except Exception as e:
				rootLogger.critical(e)
				pass

	def tryDelComment(self):
		try:
			if(loginFlag):
				rootLogger.info("Initializing comment delete process..")
				self.get_service_code(self.userId, 'comment')

				self.buttonDisable()
				self.btn_delComment.setText("댓글 삭제 중..")
				self.commentDelThr = (threading.Thread(target=self.delComment, args=(SESS, self.userId, service_code)))
				self.commentDelThr.start()
				rootLogger.info("Comment delete process started")
			else:
				rootLogger.warning("Can't delete comment without login")
				QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
		except Exception as e:
			rootLogger.critical(e)
			pass

	def delComment(self, SESS, userId, service_code):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/comment" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					rootLogger.info("All comments are deleted successfully")
					self.buttonEnable()
					self.btn_delComment.setText("댓글 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[0]["data-no"]
				del content_form[0]
				deleteData = {
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(0.5)
			except Exception as e:
				rootLogger.critical(e)
				pass

	def tryDelScrap(self):
		try:
			if(loginFlag):
				rootLogger.info("Initializing scrap delete process..")
				self.get_service_code(self.userId, 'scrap')

				self.buttonDisable()
				self.btn_delScrap.setText("스크랩 삭제 중..")
				self.scrapDelThr = (threading.Thread(target=self.delScrap, args=(SESS, self.userId, service_code)))
				self.scrapDelThr.start()
				rootLogger.info("Scrap delete process started")
			else:
				rootLogger.warning("Can't delete scrap without login")
				QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
		except Exception as e:
			rootLogger.critical(e)
			pass

	def delScrap(self, SESS, userId, service_code):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/scrap" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					rootLogger.info("All scraps are deleted successfully")
					self.buttonEnable()
					self.btn_delScrap.setText("스크랩 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[0]["data-no"]
				del content_form[0]
				deleteData = {
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(0.5)
			except Exception as e:
				rootLogger.critical(e)
				pass

	def tryDelGuestbook(self):
		try:
			if(loginFlag):
				rootLogger.info("Initializing guestbook delete process..")
				req = SESS.get("https://gallog.dcinside.com/%s/guestbook" % self.userId)
				soup = BeautifulSoup(req.text,"lxml")

				self.buttonDisable()
				self.btn_delGuestbook.setText("방명록 삭제 중..")
				self.guestbookDelThr = (threading.Thread(target=self.delGuestbook, args=(SESS, self.userId)))
				self.guestbookDelThr.start()
				rootLogger.info("Guestbook delete process started")
			else:
				rootLogger.warning("Can't delete guestbook without login")
				QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
		except Exception as e:
			rootLogger.critical(e)
			pass

	def delGuestbook(self, SESS, userId):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/guestbook" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					rootLogger.info("All guestbooks are deleted successfully")
					self.buttonEnable()
					self.btn_delGuestbook.setText("방명록 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[0]["data-headnum"]
				del content_form[0]
				deleteData = {
					"headnum" : dataNo
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/guestbook_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(0.5)
			except Exception as e:
				rootLogger.critical(e)
				pass

	def gangsin(self, SESS, userId):
		rootLogger.debug("Refreshing gallog activities..")
		global exitFlag, loginFlag
		while exitFlag == False and loginFlag == True:
			try:
				req = SESS.get("https://gallog.dcinside.com/%s" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				self.lbl_status.setText("로그인 상태 : %s" % soup.find("div", class_="galler_info").text.split("(")[0].replace("\n", ""))
				req = SESS.get("https://gallog.dcinside.com/%s" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				self.lbl_post.setText("게시글 수 : %s" % soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", ""))
				self.lbl_comment.setText("댓글 수 : %s" % soup.find_all("h2", class_="tit")[1].find("span", class_="num").text.replace("(", "").replace(")", ""))
				self.lbl_scrap.setText("스크랩 수 : %s" % soup.find_all("h2", class_="tit")[2].find("span", class_="num").text.replace("(", "").replace(")", ""))
				self.lbl_guestbook.setText("방명록 수 : %s" % soup.find_all("h2", class_="tit")[3].find("span", class_="num").text.replace("(", "").replace(")", ""))
				time.sleep(0.3)
				if not (exitFlag or loginFlag):
					self.lbl_status.setText("로그인 상태 : 로그인되지 않음")
					self.lbl_post.setText("게시글 수 : 알 수 없음")
					self.lbl_comment.setText("댓글 수 : 알 수 없음")
					self.lbl_scrap.setText("스크랩 수 : 알 수 없음")
					self.lbl_guestbook.setText("방명록 수 : 알 수 없음")
			except Exception as e:
				rootLogger.critical(e)
				pass

	def get_service_code(self, userId, purpose):
		req = SESS.get("https://gallog.dcinside.com/%s/%s" % (userId, purpose))
		soup = BeautifulSoup(req.text,"lxml")
		service_code_origin = soup.find("input", {"name" : "service_code"})["value"]
		data  = soup.select("script")[29]

		cut_1 = "var _r = _d"
		cut_2 = '<script type="text/javascript">'
		cut_3 = "</script>"

		cut_data = str(data).replace(cut_1,"")
		cut_data = str(cut_data).replace(cut_2,"")
		cut_data = str(cut_data).replace(cut_3,"")
		_r = re.sub("\n","",str(cut_data))
		r_value = re.sub("['();]","",str(_r))
		r_value = str(r_value)

		global service_code
		service_code = decode_service_code(service_code_origin, r_value)
		rootLogger.info("Service code has created")

	def buttonDisable(self):
		self.btn_delPost.setEnabled(False)
		self.btn_delComment.setEnabled(False)
		self.btn_delScrap.setEnabled(False)
		self.btn_delGuestbook.setEnabled(False)
		self.btn_cancelDelProcess.setEnabled(True)
		rootLogger.info("All buttons are disabled except cancelDelProcess")

	def buttonEnable(self):
		self.btn_delPost.setEnabled(True)
		self.btn_delPost.setText("게시글 삭제")
		self.btn_delComment.setEnabled(True)
		self.btn_delComment.setText("댓글 삭제")
		self.btn_delScrap.setEnabled(True)
		self.btn_delScrap.setText("스크랩 삭제")
		self.btn_delGuestbook.setEnabled(True)
		self.btn_delGuestbook.setText("방명록 삭제")
		self.btn_cancelDelProcess.setEnabled(False)
		rootLogger.info("All buttons are enabled except cancelDelProcess")

	def cancelDelProcess(self):
		if (loginFlag):
			global deleteFlag
			deleteFlag = False
			self.buttonEnable()
			rootLogger.info("Delete process has stopped by user's request")
		else:
			rootLogger.warning("Can't delete comment without login")
			QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)

	def checkUpdate(self):
		global VERSION, UPDATE_URL
		rootLogger.info("Checking if new version is available..")
		try:
			data = requests.get(url=UPDATE_URL).json()
			if version.parse(VERSION) < version.parse(data['version']):
				rootLogger.info("New version %s is available!" % data['version'])
				GIT_RELEASE_URL = "https://github.com/augustapple/ThanosCleaner/releases/%s" % data['version']
				QMessageBox.information(self, "업데이트 발견", "업데이트가 발견되었습니다!<br>다운로드: <a href='%s'>ThanosCleaner %s</a>" % (GIT_RELEASE_URL, data['version']), QMessageBox.Yes)
			else:
				rootLogger.info("No updates available.")
				QMessageBox.information(self, "최신 버전입니다", "업데이트가 발견되지 않았습니다.", QMessageBox.Yes)
		except Exception as e:
			rootLogger.critical(e)
			pass

class DCleanerGUI(QMainWindow):
	def __init__(self):
		super().__init__()
		wg = MyWidget()
		self.setCentralWidget(wg)

		infoMenu = QAction(QIcon("./dependencies/image/question.ico"), "&Info", self)
		rootLogger.info("Question icon loaded successfully")
		infoMenu.setShortcut("Ctrl+I")
		infoMenu.setStatusTip("프로그램 정보 표시")
		infoMenu.triggered.connect(self.showProgInfo)
		exitMenu = QAction(QIcon("./dependencies/image/shutdown.ico"), "&Exit", self)
		rootLogger.info("Exit icon loaded successfully")
		exitMenu.setShortcut("Ctrl+Q")
		exitMenu.setStatusTip("프로그램 종료")
		exitMenu.triggered.connect(self.closeEventForShortcut)

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu("&Menu")
		fileMenu.addAction(infoMenu)
		fileMenu.addAction(exitMenu)

		self.setWindowTitle("ThanosCleaner")
		self.setWindowIcon(QIcon("./dependencies/image/Thanos.ico"))
		scaling = self.logicalDpiX() / 96.0
		rootLogger.info("Set DPI Scaling to %f" % scaling)
		self.setFixedSize(300 * scaling, 400 * scaling)
		self.setStyleSheet("font-size: %dpt;" % (9 * scaling))
		self.show()

	def showProgInfo(self):
		infoBox = QMessageBox()
		infoBox.information(self, "정보", "제작자 : 작은사과나무<br>깃허브 : <a href='https://github.com/augustapple'>https://github.com/augustapple</a><br>이메일 : augustapple77@gmail.com")

	def closeEvent(self, event):
		close = QMessageBox.question(self, "프로그램 종료", "클리너를 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
		if close == QMessageBox.Yes:
			global exitFlag
			exitFlag = True
			event.accept()
			rootLogger.info("Program terminated successfully")
		else:
			event.ignore()
			rootLogger.info("Program terminate has canceled")

	def closeEventForShortcut(self):
		close = QMessageBox.question(self, "프로그램 종료", "클리너를 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
		if close == QMessageBox.Yes:
			global exitFlag
			exitFlag = True
			QCoreApplication.instance().quit()
			rootLogger.info("Program terminated successfully")
		else:
			rootLogger.info("Program terminate has canceled")
			pass

def isUserAdmin():
	try:
		if os.name == 'nt':
			return ctypes.windll.shell32.IsUserAnAdmin()
		else:
			return True
	except:
		return False

if isUserAdmin():
	os.makedirs("./logs", exist_ok=True)
	rootLogger = logging.getLogger("Cleaner")
	rootLogger.setLevel(logging.DEBUG)
	formatter = logging.Formatter("[%(asctime)s | %(levelname)s | %(name)s | Line %(lineno)s] > %(message)s", "%Y-%m-%d %H:%M:%S")
	now = time.localtime()
	fileHandler = logging.FileHandler("./logs/thanoscleaner_%d_%d_%d_%d_%d_%d.log" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
	fileHandler.setFormatter(formatter)
	fileHandler.setLevel(logging.NOTSET)
	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)
	rootLogger.addHandler(fileHandler)
	rootLogger.addHandler(streamHandler)
	if __name__ == "__main__":
		app = QApplication(sys.argv)
		main = DCleanerGUI()
		main.show()
		sys.exit(app.exec_())
else:
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
