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
		self.lbl_pw = QLabel("PW : ", self)
		self.qle_pw = QLineEdit(self)
		self.qle_pw.returnPressed.connect(self.tryLogin)
		self.cbx_pw = QCheckBox("숨김", self)
		self.cbx_pw.stateChanged.connect(self.hidePassword)
		self.cbx_pw.toggle()
		self.btn_login = QPushButton("로그인", self)
		self.btn_login.clicked.connect(self.tryLogin)
		self.btn_login.setStatusTip("로그인하기")
		self.status = "로그인되지 않음"
		self.lbl_status = QLabel("로그인 상태 : %s" % self.status, self)
		self.lbl_post = QLabel("게시글 수 : 알 수 없음")
		self.lbl_comment = QLabel("댓글 수 : 알 수 없음")
		self.btn_delpost = QPushButton("게시글 삭제", self)
		self.btn_delpost.clicked.connect(self.tryDelPost)
		self.btn_delpost.setStatusTip("모든 게시글 삭제")
		self.btn_delcomment = QPushButton("댓글 삭제", self)
		self.btn_delcomment.clicked.connect(self.tryDelComment)
		self.btn_delcomment.setStatusTip("모든 댓글 삭제")

		self.setLayout(layout)

		layout.addWidget(self.lbl_id, 1, 1)
		layout.addWidget(self.qle_id, 1, 2)
		layout.addWidget(self.lbl_pw, 2, 1)
		layout.addWidget(self.qle_pw, 2, 2)
		layout.addWidget(self.cbx_pw, 2, 3)
		layout.addWidget(self.btn_login, 3, 2)
		layout.addWidget(self.lbl_status, 4, 2, 1, 3)
		layout.addWidget(self.lbl_post, 5, 2)
		layout.addWidget(self.lbl_comment, 6, 2)
		layout.addWidget(self.btn_delpost, 7, 2)
		layout.addWidget(self.btn_delcomment, 8, 2)
	
	def hidePassword(self, state):
		if state == Qt.Checked:
			self.qle_pw.setEchoMode(QLineEdit.Password)
			self.cbx_pw.setStatusTip("비밀번호 보이기")
		else:
			self.qle_pw.setEchoMode(QLineEdit.Normal)
			self.cbx_pw.setStatusTip("비밀번호 숨기기")
	
	def tryLogin(self):
		self.userId = self.qle_id.text()
		self.userPw = self.qle_pw.text()

		loginSess = self.login(self.userId, self.userPw)

		if(self.userId == "" and self.userPw == "") or not loginSess:
			self.loginFailed = QMessageBox.warning(self, "경고", "로그인 실패", QMessageBox.Yes)
			pass
		else:
			global loginFlag
			loginFlag = True
			self.btn_login.setEnabled(False)
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

			self.btn_delcomment.setEnabled(False)
			self.btn_delpost.setEnabled(False)
			self.btn_delpost.setText("게시글 삭제 중..")
			postDelThr = (threading.Thread(target=self.delPost, args=(SESS, self.userId, service_code)))
			postDelThr.start()
		else:
			self.loginFirst = QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
	
	def delPost(self, SESS, userId, service_code):
		global exitFlag
		while not exitFlag:
			try:
				req = SESS.get("https://gallog.dcinside.com/%s/posting" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")
				
				if not content_form:
					self.btn_delpost.setEnabled(True)
					self.btn_delcomment.setEnabled(True)
					self.btn_delpost.setText("게시글 삭제")
					print("삭제할 게시글 없음")
					break
				else:
					pass
				
				delete_set = []	
				
				for i in content_form:
					data_no = (i.attrs["data-no"])
					delete_set.append(data_no)
					
				for set in delete_set:
					if exitFlag:
						break
					delete_data = {
						"no" : set,
						"service_code" : service_code
					}
					
					time.sleep(0.5)
					req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=delete_data, timeout=10)
					result = req.text
					print(result)
				
				delete_set.clear()
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

			self.btn_delcomment.setEnabled(False)
			self.btn_delpost.setEnabled(False)
			self.btn_delcomment.setText("댓글 삭제 중..")
			commentDelThr = (threading.Thread(target=self.delComment, args=(SESS, self.userId, service_code)))
			commentDelThr.start()
		else:
			self.loginFirst = QMessageBox.warning(self, "경고", "로그인을 해주세요", QMessageBox.Yes)
	
	def delComment(self, SESS, userId, service_code):
		global exitFlag
		while not exitFlag:
			try:
				req = SESS.get("https://gallog.dcinside.com/%s/comment" % userId)
				soup = BeautifulSoup(req.text,"lxml")
				content_form = soup.select("ul.cont_listbox > li")

				if not content_form:
					self.btn_delpost.setEnabled(True)
					self.btn_delcomment.setEnabled(True)
					self.btn_delcomment.setText("댓글 삭제")
					print("삭제할 댓글 없음")
					break
				else:
					pass

				delete_set = []

				for i in content_form:
					data_no = (i.attrs["data-no"])
					delete_set.append(data_no)

				for set in delete_set:
					if exitFlag:
						break
					delete_data = {
						"no" : set,
						"service_code" : service_code
					}

					time.sleep(0.5)
					req = SESS.post("https://gallog.dcinside.com/%s/ajax/log_list_ajax/delete" % userId, data=delete_data, timeout=10)
					result = req.text
					print(result)
				delete_set.clear()

			except Exception as e:
				print(e)
				pass
	
	def gangsin(self, SESS, userId):
		req = SESS.get("https://gallog.dcinside.com/%s" % userId)
		soup = BeautifulSoup(req.text,"lxml")
		self.lbl_status.setText("로그인 상태 : %s" % soup.find("div", class_="galler_info").text.split("(")[0].replace("\n", ""))
		global exitFlag
		while not exitFlag:
			req = SESS.get("https://gallog.dcinside.com/%s" % userId)
			soup = BeautifulSoup(req.text,"lxml")
			self.lbl_post.setText("게시글 수 : %s" % soup.find_all("h2", class_="tit")[0].find("span", class_="num").text.replace("(", "").replace(")", ""))
			self.lbl_comment.setText("댓글 수 : %s" % soup.find_all("h2", class_="tit")[1].find("span", class_="num").text.replace("(", "").replace(")", ""))
			time.sleep(1)

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
		self.setFixedSize(300, 250)
		self.show()
	
	def showProgInfo(self):
		infoBox = QMessageBox()
		infoBox.information(self, "정보", "제작자 : 작은사과나무\n깃허브 : https://github.com/augustapple\n이메일 : augustapple77@gmail.com")
	
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