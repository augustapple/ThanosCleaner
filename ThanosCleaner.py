from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from packaging import version
import os
import re
import sys
import time
import math
import js2py
import ctypes
import zipfile
import requests
import threading
import webbrowser
import subprocess
import logging
import logging.handlers
from bs4 import BeautifulSoup

loginFlag = False
exitFlag = False
deleteFlag = False
updateFlag = False
sleepTime = 0.33
CUR_VERSION = "3.0.1"
LATEST_VERSION = requests.get(url="https://github.com/augustapple/ThanosCleaner/raw/master/version.json").json()['version']

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

def checkUpdate():
	global CUR_VERSION, LATEST_VERSION, updateFlag
	try:
		msg = QMessageBox()
		msg.setWindowIcon(QIcon(resourcePath("dependencies/image/update.ico")))
		GIT_RELEASE_URL = "https://github.com/augustapple/ThanosCleaner/releases/tag/v%s" % LATEST_VERSION
		rootLogger.info("Checking if new version is available..")
		if sys.platform == "win32": #if OS is windows
			if version.parse(CUR_VERSION) < version.parse(LATEST_VERSION):
				rootLogger.info("New version (%s) is available!" % LATEST_VERSION)
				msg.setWindowTitle("업데이트 발견")
				msg.setText("업데이트가 발견되었습니다!<br>현재 버전 : %s<br>최신 버전 : %s" % (CUR_VERSION, LATEST_VERSION))
				msg.addButton(QPushButton("Update"), QMessageBox.YesRole)
				msg.setStandardButtons(QMessageBox.Cancel)
				update = msg.exec_()
				if update == QMessageBox.Cancel:
					rootLogger.info("Update is available but canceled by user")
				else:
					rootLogger.info("Update started")
					threading.Thread(target=startUpdate).start()
					updateFlag = True
			else:
				rootLogger.info("No updates available.")
				msg.setStyleSheet("QLabel{min-width: 150px;}")
				msg.setWindowTitle("업데이트 없음")
				msg.setText("최신 버전입니다<br>현재 버전 : %s" % CUR_VERSION)
				msg.setStandardButtons(QMessageBox.Yes)
				msg.exec_()
		else: #if OS is not windows
			if version.parse(CUR_VERSION) < version.parse(LATEST_VERSION):
				rootLogger.info("New version (%s) is available!" % LATEST_VERSION)
				msg.setWindowTitle("업데이트 발견")
				msg.setText("업데이트가 발견되었습니다!<br>현재 버전 : %s<br>최신 버전 : <a href='%s'>%s</a>" % (CUR_VERSION, GIT_RELEASE_URL, LATEST_VERSION))
				msg.exec_()
			else:
				rootLogger.info("No updates available.")
				msg.setStyleSheet("QLabel{min-width: 150px;}")
				msg.setWindowTitle("업데이트 없음")
				msg.setText("업데이트가 발견되지 않았습니다<br>현재 버전 : %s" % CUR_VERSION)
				msg.setStandardButtons(QMessageBox.Yes)
				msg.exec_()

	except Exception as e:
		rootLogger.critical(e)
		pass

def startUpdate():
	global CUR_VERSION, LATEST_VERSION
	try:
		rootLogger.info("v%s download started..." % LATEST_VERSION)
		DOWNLOAD_URL = "https://github.com/augustapple/ThanosCleaner/releases/download/v%s/ThanosCleaner.zip" % LATEST_VERSION
		fileBin = requests.get(DOWNLOAD_URL)
		rootLogger.info("v%s download complete" % LATEST_VERSION)

		if not os.path.exists("C:/Temp"):
			os.makedirs("C:/Temp")
			rootLogger.info("Temp directory has created")
		else:
			rootLogger.info("Temp directory has already exist")

		with open("C:/Temp/ThanosCleaner.zip", "wb") as f:
			f.write(fileBin.content)
			rootLogger.info("Successfully Wrote downloaded binary to file")

		newVersionZip = zipfile.ZipFile("C:/Temp/ThanosCleaner.zip")
		newVersionZip.extract("ThanosCleaner.exe", "C:/Temp/")
		rootLogger.info("Extract complete")
		subprocess.Popen(resourcePath("dependencies/update.bat"))
		rootLogger.info("update.bat has executed")
		global exitFlag
		exitFlag = True
		QCoreApplication.instance().quit()

	except Exception as e:
		rootLogger.critical(e)
		pass

class MyWidget(QWidget):
	def __init__(self):
		super().__init__()
		try:
			rootLogger.debug("Application started")

			layout = QVBoxLayout()
			loginGroupBox = QGroupBox("로그인")
			gallGroupBox = QGroupBox("갤러리별 삭제")
			accountGroupBox = QGroupBox("계정별 삭제")

			self.qle_id = QLineEdit(self)
			self.qle_id.setPlaceholderText("아이디")
			self.qle_id.returnPressed.connect(self.tryLogin)
			self.qle_pw = QLineEdit(self)
			self.qle_pw.setPlaceholderText("비밀번호")
			self.qle_pw.returnPressed.connect(self.tryLogin)
			self.cbx_pw = QCheckBox("비밀번호 숨김", self)
			self.cbx_pw.stateChanged.connect(self.hidePassword)
			self.cbx_pw.toggle()
			self.cbx_sm = QCheckBox("슬로우 모드", self)
			self.cbx_sm.stateChanged.connect(self.slowMode)
			self.btn_login = QPushButton("로그인", self)
			self.btn_login.clicked.connect(self.tryLogin)
			self.btn_login.setStatusTip("로그인하기")
			self.btn_logout = QPushButton("로그아웃", self)
			self.btn_logout.setEnabled(False)
			self.btn_logout.clicked.connect(self.logout)
			self.btn_logout.setStatusTip("로그아웃하기")
			self.status = "로그인되지 않음"
			self.lbl_status = QLabel("로그인 상태 : %s" % self.status, self)
			loginGbxLayout = QGridLayout()
			loginGroupBox.setLayout(loginGbxLayout)
			loginGbxLayout.addWidget(self.qle_id, 1, 2)
			loginGbxLayout.addWidget(self.qle_pw, 2, 2)
			loginGbxLayout.addWidget(self.cbx_pw, 3, 2)
			loginGbxLayout.addWidget(self.cbx_sm, 3, 3)
			loginGbxLayout.addWidget(self.btn_login, 1, 3)
			loginGbxLayout.addWidget(self.btn_logout, 2, 3)
			loginGbxLayout.addWidget(self.lbl_status, 6, 2, 1, 3)
			layout.addWidget(loginGroupBox)

			self.cmb_sort = QComboBox(self)
			self.cmb_sort.addItem("최신순")
			self.cmb_sort.addItem("옛날순")
			middleLayout = QHBoxLayout()
			middleLayout.addWidget(self.cmb_sort)
			layout.addLayout(middleLayout)
			
			self.cmb_gall = QComboBox(self)
			self.cmb_gall.setEnabled(False)
			self.lbl_post = QLabel("게시글 수 : 알 수 없음")
			self.btn_delPost = QPushButton("게시글 삭제", self)
			self.btn_delPost.clicked.connect(self.tryDelPost)
			self.btn_delPost.setStatusTip("모든 게시글 삭제")
			self.lbl_comment = QLabel("댓글 수 : 알 수 없음")
			self.btn_delComment = QPushButton("댓글 삭제", self)
			self.btn_delComment.clicked.connect(self.tryDelComment)
			self.btn_delComment.setStatusTip("모든 댓글 삭제")
			gallGbxLayout = QGridLayout()
			gallGroupBox.setLayout(gallGbxLayout)
			gallGbxLayout.addWidget(self.cmb_gall, 1, 1, 1, 2)
			gallGbxLayout.addWidget(self.lbl_post, 2, 1)
			gallGbxLayout.addWidget(self.btn_delPost, 2, 2)
			gallGbxLayout.addWidget(self.lbl_comment, 3, 1)
			gallGbxLayout.addWidget(self.btn_delComment, 3, 2)
			layout.addWidget(gallGroupBox)

			self.lbl_scrap = QLabel("스크랩 수 : 알 수 없음")
			self.btn_delScrap = QPushButton("스크랩 삭제", self)
			self.btn_delScrap.clicked.connect(self.tryDelScrap)
			self.btn_delScrap.setStatusTip("모든 스크랩 삭제")
			self.lbl_guestbook = QLabel("방명록 수 : 알 수 없음")
			self.btn_delGuestbook = QPushButton("방명록 삭제", self)
			self.btn_delGuestbook.clicked.connect(self.tryDelGuestbook)
			self.btn_delGuestbook.setStatusTip("모든 방명록 삭제")
			accountGbxLayout = QGridLayout()
			accountGroupBox.setLayout(accountGbxLayout)
			accountGbxLayout.addWidget(self.lbl_scrap, 1, 1)
			accountGbxLayout.addWidget(self.btn_delScrap, 1, 2)
			accountGbxLayout.addWidget(self.lbl_guestbook, 2, 1)
			accountGbxLayout.addWidget(self.btn_delGuestbook, 2, 2)
			layout.addWidget(accountGroupBox)

			self.btn_cancelDelProcess = QPushButton("삭제 중단", self)
			self.btn_cancelDelProcess.setEnabled(False)
			self.btn_cancelDelProcess.clicked.connect(self.cancelDelProcess)
			self.btn_cancelDelProcess.setStatusTip("진행 중인 삭제 작업 중단")
			bottomLayout = QHBoxLayout()
			bottomLayout.addWidget(self.btn_cancelDelProcess)
			layout.addLayout(bottomLayout)

			self.setLayout(layout)

			rootLogger.debug("Application initialized successfully")
			checkUpdate()
		except Exception as e:
			rootLogger.critical(e)
			pass


	def hidePassword(self, state):
		if state == Qt.Checked:
			self.qle_pw.setEchoMode(QLineEdit.Password)
			self.cbx_pw.setStatusTip("비밀번호 보이기")
			rootLogger.info("Hide password is enabled")
		else:
			self.qle_pw.setEchoMode(QLineEdit.Normal)
			self.cbx_pw.setStatusTip("비밀번호 숨기기")
			rootLogger.info("Hide password is disabled")
	
	def slowMode(self, state):
		global sleepTime
		if state == Qt.Checked:
			sleepTime = 1.65
			rootLogger.info("Slowmode is enabled")
		else:
			sleepTime = 0.33
			rootLogger.info("Slowmode is disabled")

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
				self.cmb_gall.clear()
				self.cmb_gall.setEnabled(False)
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
			self.cmb_gall.clear()
			self.cmb_gall.setEnabled(False)
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
				gangsinThr = (threading.Thread(target=self.gangsin, args=(SESS, self.userId))).start()
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
			self.cmb_gall.addItem("전체 갤러리")
			self.getGalleryList(SESS, userId)
			return SESS

	def getGalleryList(self, SESS, userId):
		try:
			req = SESS.get("https://gallog.dcinside.com/%s/posting" % userId)
			soup = BeautifulSoup(req.text, "lxml")
			postGallList = soup.select("ul.option_box > li")
			req = SESS.get("https://gallog.dcinside.com/%s/comment" % userId)
			soup = BeautifulSoup(req.text, "lxml")
			commentGallList = soup.select("ul.option_box > li")
			self.gallDict = {}
			for i in postGallList:
				self.gallDict[i.text] = [i.get("data-value"), i.get("onclick").replace("posting", "type").replace("comment", "type")]
			for i in commentGallList:
				self.gallDict[i.text] = [i.get("data-value"), i.get("onclick").replace("posting", "type").replace("comment", "type")]
			del self.gallDict["전체보기"]
			rootLogger.info("User's gallery list created successfully")
			gallNameList = self.gallDict.keys()
			for i in gallNameList:
				self.cmb_gall.addItem("%s" % i)
			self.cmb_gall.setEnabled(True)
		except Exception as e:
			rootLogger.critical(e)
			pass

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
		global exitFlag, loginFlag, deleteFlag, sleepTime
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				if self.cmb_sort.currentText() == "최신순":
					pageNum = 1
					btnIndex = 0
				else:
					pageNum = math.ceil(int(self.lbl_post.text().split(" ")[-1]) / 20)
					btnIndex = -1
				if self.cmb_gall.currentText() == "전체 갤러리":
					req = SESS.get("https://gallog.dcinside.com/%s/posting?p=%d" % (userId, pageNum))
				else:
					url = "https://gallog.dcinside.com" + self.gallDict[self.cmb_gall.currentText()][1].replace("type", "posting").replace("location.href='", "")[:-1] + "&p=%d" % pageNum
					req = SESS.get(url)
				soup = BeautifulSoup(req.text, "lxml")
				content_form = soup.select("ul.cont_listbox > li")
				ci_t = SESS.cookies.get_dict()['ci_c']

				if not content_form:
					rootLogger.info("All posts are deleted successfully")
					self.buttonEnable()
					self.btn_delPost.setText("게시글 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[btnIndex]["data-no"]
				del content_form[btnIndex]
				deleteData = {
					"ci_t" : ci_t,
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(sleepTime)
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
		global exitFlag, loginFlag, deleteFlag, sleepTime
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				if self.cmb_sort.currentText() == "최신순":
					pageNum = 1
					btnIndex = 0
				else:
					pageNum = math.ceil(int(self.lbl_comment.text().split(" ")[-1]) / 20)
					btnIndex = -1
				if self.cmb_gall.currentText() == "전체 갤러리":
					req = SESS.get("https://gallog.dcinside.com/%s/comment?p=%d" % (userId, pageNum))
				else:
					url = "https://gallog.dcinside.com" + self.gallDict[self.cmb_gall.currentText()][1].replace("type", "comment").replace("location.href='", "")[:-1] + "&p=%d" % pageNum
					req = SESS.get(url)
				soup = BeautifulSoup(req.text, "lxml")
				content_form = soup.select("ul.cont_listbox > li")
				ci_t = SESS.cookies.get_dict()['ci_c']

				if not content_form:
					rootLogger.info("All comments are deleted successfully")
					self.buttonEnable()
					self.btn_delComment.setText("댓글 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[btnIndex]["data-no"]
				del content_form[btnIndex]
				deleteData = {
					"ci_t" : ci_t,
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(sleepTime)
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
		global exitFlag, loginFlag, deleteFlag, sleepTime
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				if self.cmb_sort.currentText() == "최신순":
					pageNum = 1
					btnIndex = 0
				else:
					pageNum = math.ceil(int(self.lbl_post.text().split(" ")[-1]) / 20)
					btnIndex = -1
				req = SESS.get("https://gallog.dcinside.com/%s/scrap?p=%d" % (userId, pageNum))
				soup = BeautifulSoup(req.text, "lxml")
				content_form = soup.select("ul.cont_listbox > li")
				ci_t = SESS.cookies.get_dict()['ci_c']

				if not content_form:
					rootLogger.info("All scraps are deleted successfully")
					self.buttonEnable()
					self.btn_delScrap.setText("스크랩 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[btnIndex]["data-no"]
				del content_form[btnIndex]
				deleteData = {
					"ci_t" : ci_t,
					"no" : dataNo,
					"service_code" : service_code
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(sleepTime)
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
		global exitFlag, loginFlag, deleteFlag, sleepTime
		deleteFlag = True
		while exitFlag == False and deleteFlag == True:
			try:
				if not loginFlag:
					break
				if self.cmb_sort.currentText() == "최신순":
					pageNum = 1
					btnIndex = 0
				else:
					pageNum = math.ceil(int(self.lbl_post.text().split(" ")[-1]) / 20)
					btnIndex = -1
				req = SESS.get("https://gallog.dcinside.com/%s/guestbook?p=%d" % (userId, pageNum))
				soup = BeautifulSoup(req.text, "lxml")
				content_form = soup.select("ul.cont_listbox > li")
				ci_t = SESS.cookies.get_dict()['ci_c']

				if not content_form:
					rootLogger.info("All guestbooks are deleted successfully")
					self.buttonEnable()
					self.btn_delGuestbook.setText("방명록 삭제")
					deleteFlag = False
					break
				else:
					pass

				dataNo = content_form[btnIndex]["data-headnum"]
				del content_form[btnIndex]
				deleteData = {
					"ci_t" : ci_t,
					"headnum" : dataNo
				}
				req = SESS.post("https://gallog.dcinside.com/%s/ajax/guestbook_ajax/delete" % userId, data=deleteData, timeout=10)
				rootLogger.debug(req.text)
				time.sleep(sleepTime)
			except Exception as e:
				rootLogger.critical(e)
				pass

	def gangsin(self, SESS, userId):
		rootLogger.debug("Refreshing gallog activities..")
		global exitFlag, loginFlag
		try:
			self.postNum = 0
			self.commentNum = 0
			self.etcList = []
			while exitFlag == False and loginFlag == True:
				self.gangsinPostThr = (threading.Thread(target=self.gangsinPost, args=(SESS, userId)))
				self.gangsinPostThr.start()
				self.gangsinCommentThr = (threading.Thread(target=self.gangsinComment, args=(SESS, userId)))
				self.gangsinCommentThr.start()
				self.gangsinEtcThr = (threading.Thread(target=self.gangsinEtc, args=(SESS, userId)))
				self.gangsinEtcThr.start()
				self.gangsinPostThr.join()
				self.gangsinCommentThr.join()
				self.gangsinEtcThr.join()
				self.lbl_status.setText("로그인 상태 : %s" % self.etcList[0])
				self.lbl_post.setText("게시글 수 : %d" % self.postNum)
				self.lbl_comment.setText("댓글 수 : %d" % self.commentNum)
				self.lbl_scrap.setText("스크랩 수 : %d" % self.etcList[1])
				self.lbl_guestbook.setText("방명록 수 : %d" % self.etcList[2])
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

	def gangsinPost(self, SESS, userId):
		try:
			postNum = 0
			try:
				if self.cmb_gall.currentText() == "전체 갤러리":
					url = "https://gallog.dcinside.com/%s" % userId
					req = SESS.get(url)
					soup = BeautifulSoup(req.text, "lxml")
					postNum = soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", "")
				else:
					url = "https://gallog.dcinside.com" + self.gallDict[self.cmb_gall.currentText()][1].replace("type", "posting").replace("location.href='", "")[:-1]
					req = SESS.get(url)
					soup = BeautifulSoup(req.text, "lxml")
					postNum = soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", "")
			except IndexError:
				postNum = 0
				pass
			self.postNum = int(postNum.replace(",", ""))
		except Exception as e:
			rootLogger.critical(e)
			pass

	def gangsinComment(self, SESS, userId):
		try:
			commentNum = 0
			try:
				if self.cmb_gall.currentText() == "전체 갤러리":
					url = "https://gallog.dcinside.com/%s" % userId
					req = SESS.get(url)
					soup = BeautifulSoup(req.text, "lxml")
					commentNum = soup.find_all("h2", class_="tit")[1].find("span", class_="num").text.replace("(", "").replace(")", "")
				else:
					url = "https://gallog.dcinside.com" + self.gallDict[self.cmb_gall.currentText()][1].replace("type", "comment").replace("location.href='", "")[:-1]
					req = SESS.get(url)
					soup = BeautifulSoup(req.text, "lxml")
					commentNum = soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", "")
			except IndexError:
				commentNum = 0
				pass
			self.commentNum = int(commentNum.replace(",", ""))
		except Exception as e:
			rootLogger.critical(e)
			pass

	def gangsinEtc(self, SESS, userId):
		try:
			etcList = []
			url = "https://gallog.dcinside.com/%s" % userId
			req = SESS.get(url)
			soup = BeautifulSoup(req.text, "lxml")
			etcList.append(soup.find("div", class_="galler_info").text.split("(")[0].replace("\n", ""))
			etcList.append(int(soup.find_all("h2", class_="tit")[2].find("span", class_="num").text.replace("(", "").replace(")", "").replace(",", "")))
			etcList.append(int(soup.find_all("h2", class_="tit")[3].find("span", class_="num").text.replace("(", "").replace(")", "").replace(",", "")))
			self.etcList = etcList
		except Exception as e:
			rootLogger.critical(e)
			pass

	def get_service_code(self, userId, purpose):
		req = SESS.get("https://gallog.dcinside.com/%s/%s" % (userId, purpose))
		soup = BeautifulSoup(req.text, "lxml")
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
		rootLogger.info("Service code has created: %s" % service_code)

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

class ImageViewer(QMainWindow):
	def __init__(self, parent=None):
		super(ImageViewer, self).__init__(parent)
		self.setFixedSize(700, 442)
		self.setWindowTitle("귀여운 웰시코기")
		self.lbl = QLabel(self)
		self.lbl.resize(700, 442)
		image = QPixmap(resourcePath("dependencies/image/corgi.jpg"))
		self.lbl.setPixmap(QPixmap(image))
		self.show()

class DCleanerGUI(QMainWindow):
	def __init__(self):
		super().__init__()
		wg = MyWidget()
		self.setCentralWidget(wg)

		infoMenu = QAction(QIcon(resourcePath("dependencies/image/question.ico")), "&Info", self)
		rootLogger.info("Question icon loaded successfully")
		infoMenu.setShortcut("Ctrl+I")
		infoMenu.triggered.connect(self.showProgInfo)
		infoMenu.setStatusTip("프로그램 정보 표시")
		updateMenu = QAction(QIcon(resourcePath("dependencies/image/update.ico")), "&Update", self)
		rootLogger.info("Update icon loaded successfully")
		updateMenu.setShortcut("Ctrl+T")
		updateMenu.setStatusTip("업데이트 확인")
		updateMenu.triggered.connect(checkUpdate)
		exitMenu = QAction(QIcon(resourcePath("dependencies/image/shutdown.ico")), "&Exit", self)
		rootLogger.info("Exit icon loaded successfully")
		exitMenu.setShortcut("Ctrl+Q")
		exitMenu.setStatusTip("프로그램 종료")
		exitMenu.triggered.connect(self.closeEventForShortcut)
		corgiMenu = QAction(QIcon(resourcePath("dependencies/image/star.ico")), "&Corgi", self)
		corgiMenu.triggered.connect(self.showCorgiImage)
		corgiMenu.setStatusTip("귀여운 웰시코기 보기")

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu("&Menu")
		fileMenu.addAction(infoMenu)
		fileMenu.addAction(updateMenu)
		fileMenu.addAction(exitMenu)
		fileMenu.addAction(corgiMenu)

		self.setWindowTitle("ThanosCleaner")
		self.setWindowIcon(QIcon(resourcePath("dependencies/image/Thanos.ico")))
		if sys.platform == "darwin" or sys.platform == "linux":
			scalingSize = self.logicalDpiX() / 72.0
			rootLogger.info("Set DPI Scaling to %f" % scalingSize)
			self.setFixedSize(300 * scalingSize, 450 * scalingSize)
			self.setStyleSheet("font-size: %dpx;" % (12 * scalingSize))
		else:
			scalingSize = self.logicalDpiX() / 96.0
			rootLogger.info("Set DPI Scaling to %f" % scalingSize)
			self.setFixedSize(300 * scalingSize, 450 * scalingSize)
			self.setStyleSheet("font-size: %dpx;" % (12 * scalingSize))
		
		global updateFlag
		if not updateFlag:
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
	
	def showCorgiImage(self):
		self.dialog = ImageViewer(self)

def resourcePath(relativePath):
	try:
		basePath = sys._MEIPASS
	except Exception:
		basePath = os.path.abspath(".")
	return os.path.join(basePath, relativePath)

def isUserAdmin():
	try:
		if os.name == 'nt':
			return ctypes.windll.shell32.IsUserAnAdmin()
		else:
			return True
	except:
		return False

if isUserAdmin():
	if __name__ == "__main__":
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
		app = QApplication(sys.argv)
		main = DCleanerGUI()
		sys.exit(app.exec_())
else:
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
