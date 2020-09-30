# IP 차단 안내

2020/09/29 이후로 클리너를 사용하기 위해 로그인하면 IP가 차단되는 이슈가 있습니다. 현재 배포된 3.0.4 버전은 공지하기 위해

업데이트된 버전이며 3.0.3 버전과 기능의 차이가 전혀 없습니다. 해당 문제를 해결한 3.0.5 버전이 배포되기 전에는 클리너를

사용하지 말아주시기 바랍니다. 이미 해당 이슈로 인해 IP 차단을 먹은 경우라면 ipTIME 기준 공유기 관리자 페이지에 접속하여

고급 설정 > 네트워크 관리 > 인터넷 설정 정보 탭에 들어가 MAC주소 변경에 체크를 하신 후 적용 버튼을 누르시면 IP가 변경되어

정상적으로 접속이 가능합니다.

# 버전 안내
[최신 버전 다운로드](https://github.com/augustapple/ThanosCleaner/releases/latest/download/ThanosCleaner.zip)

[이전 버전 목록](https://github.com/augustapple/ThanosCleaner/releases)

최근 업데이트 (3.0.3)

+) 서비스 코드 생성 (로그인) 과정에 있던 버그 수정.

+) 코드 가독성을 위해 beautifulsoup를 pyquery로 교체 중. (3.0.4 버전에선 완전히 이루어질 예정)

+) 게시글 댓글 표시에 있던 버그 수정.

+) 슬로우 모드가 프로그램 실행 시 기본적으로 활성화 됨.

# 디시 캡차 패치 관련 공지

현재 디시인사이드 측의 reCAPTCHA 패치로 아래 삭제 서비스는 슬로우 모드를 활성화해야 이용 가능합니다.

* 글 삭제
* 댓글 삭제

슬로우 모드로 이용 중 캡차를 감지했다는 문구가 나오면, 안내창을 따라 갤로그에 방문하여 직접 글이나 댓글을 캡차를 해제하고 삭제한 뒤 다시 클리너를 가동해주시기 바랍니다.

# 개발 안내

학업과 개인 사정으로 인해, 그리고 더이상 디시를 하지 않기 때문에 개발이 늦어질 수 있습니다.

그렇지만 보내주시는 건의 메일이나 질문들은 최대한 답변해드리고 있으니 궁금한 사항이 있으시면 언제든 메일 바랍니다.

## ThanosCleaner란?
한 번의 핑거 스냅으로 우주의 절반을 소멸시킨 타노스를 본받아 한 번의 클릭으로

당신의 디시인사이드 게시글/댓글/스크랩/방명록을 삭제해주는 디시인사이드 클리너입니다.

## ThanosCleaner의 사용법은?
[여기](https://github.com/augustapple/ThanosCleaner/releases)를 클릭하여 미리 패키징된 파일을 다운로드 하거나

아래의 명령어로 직접 패키징하여 사용할 수 있습니다.

```
# 구성요소 설치
pip install -r requirements.txt

# PyInstaller를 이용한 컴파일
pyinstaller -F -w --icon="dependencies/image/Thanos.ico" ThanosCleaner.py
```

프로그램을 실행하면 아래와 같은 화면이 나옵니다.

![UI](https://user-images.githubusercontent.com/57178921/77852076-9d792d00-7217-11ea-8940-937da022be92.png)

해당 화면에 아이디와 비밀번호를 입력하고 엔터 혹은 로그인 버튼을 눌러 로그인을 합니다.

아래와 같이 로그인이 완료되었을 경우, 게시글/댓글/스크랩/방명록 삭제 버튼을 눌러 삭제를 시작합니다.

![loginUI](https://user-images.githubusercontent.com/57178921/77852078-9e11c380-7217-11ea-9dfb-1e0f61b769df.png)

로그아웃은 언제든 가능하며, 삭제가 진행중일 경우 로그아웃을 하기 전 유저에게 확인을 묻습니다.

또한 삭제가 시작되었을 경우 삭제 중단 버튼이 활성화되어 삭제가 완료되기 전 중도 취소할 수 있는 기능을 제공합니다.

## Special Thanks

베타버전을 테스트해준 ㄴㅁㅈㄱ, 대리영정, 플링츄, 배교자 님

이슈를 제보해주신 [craftingmod](https://github.com/craftingmod) 님

스크랩, 방명록 삭제 기능을 추가해주신 [L4by](https://github.com/L4by) 님

ThanosCleaner를 직접 검수해주신 [티바이트](https://github.com/tibyte) 님

ThanosCleaner의 구조를 짜는데 도와주신 [쪼리핑](https://github.com/JJoriping) 님

## 오류가 발생했을 시
해당 리포지토리의 [Issues](https://github.com/augustapple/ThanosCleaner/issues) 또는

augustapple77@gmail.com 으로 제보해주시면 됩니다.

제보 시 클리너 폴더 내부의 `logs/thanoscleaner_YYMMDD.log` 파일을 동봉해주셔야 자세한 원인 파악 후 조치가 가능하니

꼭!! 해당 파일을 함께 보내주시기 바랍니다. 감사합니다.

