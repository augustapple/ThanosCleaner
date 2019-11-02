from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import re
import sys
import time
import js2py
import ctypes
import requests
import threading
from bs4 import BeautifulSoup

loginFlag = False
exitFlag = False
deleteFlag = False

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
		self.lbl_guestbook = QLabel("방명록 수 : 알 수 없음")
		self.btn_delPost = QPushButton("게시글 삭제", self)
		self.btn_delPost.clicked.connect(self.tryDelPost)
		self.btn_delPost.setStatusTip("모든 게시글 삭제")
		self.btn_delComment = QPushButton("댓글 삭제", self)
		self.btn_delComment.clicked.connect(self.tryDelComment)
		self.btn_delComment.setStatusTip("모든 댓글 삭제")
		self.btn_delGuestbook = QPushButton("방명록 삭제", self)
		self.btn_delGuestbook.clicked.connect(self.tryDelGuestbook)
		self.btn_delGuestbook.setStatusTip("모든 방명록 삭제")

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
		layout.addWidget(self.lbl_guestbook, 8, 2)
		layout.addWidget(self.btn_delPost, 9, 2)
		layout.addWidget(self.btn_delComment, 10, 2)
		layout.addWidget(self.btn_delGuestbook, 11, 2)
	
	def hidePassword(self, state):
		if state == Qt.Checked:
			self.qle_pw.setEchoMode(QLineEdit.Password)
			self.cbx_pw.setStatusTip("비밀번호 보이기")
		else:
			self.qle_pw.setEchoMode(QLineEdit.Normal)
			self.cbx_pw.setStatusTip("비밀번호 숨기기")
	
	def logout(self):
		global SESS, loginFlag, deleteFlag
		if deleteFlag:
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
				self.btn_delPost.setEnabled(True)
				self.btn_delPost.setText("게시글 삭제")
				self.btn_delComment.setEnabled(True)
				self.btn_delComment.setText("댓글 삭제")
				self.btn_delGuestbook.setEnabled(True)
				self.btn_delGuestbook.setText("방명록 삭제")
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
			self.btn_delPost.setEnabled(True)
			self.btn_delPost.setText("게시글 삭제")
			self.btn_delComment.setEnabled(True)
			self.btn_delComment.setText("댓글 삭제")
			self.btn_delGuestbook.setEnabled(True)
			self.btn_delGuestbook.setText("방명록 삭제")
		deleteFlag = False

	def tryLogin(self):
		self.userId = self.qle_id.text()
		self.userPw = self.qle_pw.text()

		if(self.userId == "" or self.userPw == ""):
			QMessageBox.warning(self, "경고", "아이디, 비밀번호를 입력해주세요", QMessageBox.Yes)
		else:
			loginSess = self.login(self.userId, self.userPw)
			if not loginSess:
				QMessageBox.warning(self, "경고", "로그인에 실패했습니다", QMessageBox.Yes)
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
	
	def login(self, userId, userPw):
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
			return 0
		else:
			SESS = session
			return SESS
	
	def tryDelPost(self):
		if(loginFlag):
			req = SESS.get("https://gallog.dcinside.com/%s/posting" % self.userId)
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

			service_code = decode_service_code(service_code_origin, r_value)

			self.btn_delGuestbook.setEnabled(False)
			self.btn_delComment.setEnabled(False)
			self.btn_delPost.setEnabled(False)
			self.btn_delPost.setText("게시글 삭제 중..")
			self.postDelThr = (threading.Thread(target=self.delPost, args=(SESS, self.userId, service_code)))
			self.postDelThr.start()
		else:
			QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
	
	def delPost(self, SESS, userId, service_code):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while not exitFlag:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/posting" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					self.btn_delGuestbook.setEnabled(True)
					self.btn_delPost.setEnabled(True)
					self.btn_delComment.setEnabled(True)
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
				print(req.text)
				time.sleep(0.5)
			except Exception as e:
				print(e)
				pass
	
	def tryDelComment(self):
		if(loginFlag):
			req = SESS.get("https://gallog.dcinside.com/%s/posting" % self.userId)
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

			service_code = decode_service_code(service_code_origin, r_value)

			self.btn_delGuestbook.setEnabled(False)
			self.btn_delComment.setEnabled(False)
			self.btn_delPost.setEnabled(False)
			self.btn_delComment.setText("댓글 삭제 중..")
			self.commentDelThr = (threading.Thread(target=self.delComment, args=(SESS, self.userId, service_code)))
			self.commentDelThr.start()
		else:
			QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
	
	def delComment(self, SESS, userId, service_code):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while not exitFlag:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/comment" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					self.btn_delGuestbook.setEnabled(True)
					self.btn_delPost.setEnabled(True)
					self.btn_delComment.setEnabled(True)
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
				print(req.text)
				time.sleep(0.5)
			except Exception as e:
				print(e)
				pass

	def tryDelGuestbook(self):
		if(loginFlag):
			req = SESS.get("https://gallog.dcinside.com/%s/guestbook" % self.userId)
			soup = BeautifulSoup(req.text,"lxml")

			self.btn_delComment.setEnabled(False)
			self.btn_delPost.setEnabled(False)
			self.btn_delGuestbook.setEnabled(False)
			self.btn_delGuestbook.setText("방명록 삭제 중..")
			self.commentDelThr = (threading.Thread(target=self.delGuestbook, args=(SESS, self.userId)))
			self.commentDelThr.start()
		else:
			QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
	
	def delGuestbook(self, SESS, userId):
		global exitFlag, loginFlag, deleteFlag
		deleteFlag = True
		while not exitFlag:
			try:
				if not loginFlag:
					break
				req = SESS.get("https://gallog.dcinside.com/%s/guestbook" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					self.btn_delGuestbook.setEnabled(True)
					self.btn_delPost.setEnabled(True)
					self.btn_delComment.setEnabled(True)
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
				print(req.text)
				time.sleep(0.5)
			except Exception as e:
				print(e)
				pass
	
	def gangsin(self, SESS, userId):
		global exitFlag, loginFlag
		while exitFlag == False and loginFlag == True:
			req = SESS.get("https://gallog.dcinside.com/%s" % userId)
			soup = BeautifulSoup(req.text,"lxml")
			self.lbl_status.setText("로그인 상태 : %s" % soup.find("div", class_="galler_info").text.split("(")[0].replace("\n", ""))
			req = SESS.get("https://gallog.dcinside.com/%s" % userId)
			soup = BeautifulSoup(req.text,"lxml")
			self.lbl_post.setText("게시글 수 : %s" % soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", ""))
			self.lbl_comment.setText("댓글 수 : %s" % soup.find_all("h2", class_="tit")[1].find("span", class_="num").text.replace("(", "").replace(")", ""))
			self.lbl_guestbook.setText("방명록 수 : %s" % soup.find_all("h2", class_="tit")[3].find("span", class_="num").text.replace("(", "").replace(")", ""))
			if not (exitFlag or loginFlag):
				self.lbl_status.setText("로그인 상태 : 로그인되지 않음")
				self.lbl_post.setText("게시글 수 : 알 수 없음")
				self.lbl_comment.setText("댓글 수 : 알 수 없음")
				self.lbl_guestbook.setText("방명록 수 : 알 수 없음")

class DCleanerGUI(QMainWindow):
	def __init__(self):
		super().__init__()
		wg = MyWidget()
		self.setCentralWidget(wg)
		
		infoMenu = QAction(QIcon("./dependencies/image/question.ico"), "&Info", self)
		infoMenu.setShortcut("Ctrl+I")
		infoMenu.setStatusTip("프로그램 정보 표시")
		infoMenu.triggered.connect(self.showProgInfo)
		exitMenu = QAction(QIcon("./dependencies/image/shutdown.ico"), "&Exit", self)
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
		self.setFixedSize(300 * scaling, 300 * scaling)
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
		else:
			event.ignore()
	
	def closeEventForShortcut(self):
		close = QMessageBox.question(self, "프로그램 종료", "클리너를 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
		if close == QMessageBox.Yes:
			global exitFlag
			exitFlag = True
			QCoreApplication.instance().quit()
		else:
			pass

def isUserAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if isUserAdmin():
	if __name__ == "__main__":
		app = QApplication(sys.argv)
		main = DCleanerGUI()
		main.show()
		sys.exit(app.exec_())
else:
	ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
