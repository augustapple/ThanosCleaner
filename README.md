# [**최신 버전 다운로드**](https://github.com/augustapple/ThanosCleaner/releases/latest/download/ThanosCleaner.zip)

# 바이러스 관련 공지
[관련 이슈](https://github.com/augustapple/ThanosCleaner/issues/17)

[관련 SO 질문글](https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg)

ThanosCleaner를 배포하기 위해 사용하는 pyinstaller의 특성 때문에 (미리 컴파일된 bootloader를 사용함) 바이러스로
오진한 것 같습니다.

현재 배포되고 있는 3.0.1 이상 버전은 직접 컴파일한 bootloader를 이용한 pyinstaller로 빌드되었습니다. 기존의 3.0.0 이하 버전을 사용하시던 분들 중
만약 바이러스로 분류되어 사용하지 못하신 분들은 3.0.1 이상 버전으로 업데이트 해주시기 바랍니다.

# 디시 캡차 패치 관련 공지

현재 디시인사이드 측의 reCAPTCHA 패치로 아래 삭제 서비스는 슬로우 모드를 활성화해야 이용 가능합니다.

* 글 삭제
* 댓글 삭제

활성화 후 이용 중 삭제가 더 이상 진행되지 않는다면 갤로그에 수동으로 로그인하신 후 reCAPTCHA 과정을 거쳐 글, 댓글 중 하나를 삭제하셔야 합니다.

# 개발 안내

학업과 개인 사정으로 인해, 그리고 더이상 디시를 하지 않기 때문에 개발이 늦어질 수 있습니다.

그렇지만 보내주시는 건의 메일이나 질문들은 최대한 답변해드리고 있으니 궁금한 사항이 있으시면 언제든 메일 바랍니다.

## 최근 업데이트 (3.0.3)

+) 서비스 코드 생성 (로그인) 과정에 있던 버그 수정.

+) 코드 가독성을 위해 beautifulsoup를 pyquery로 교체 중. (3.0.4 버전에선 완전히 이루어질 예정)

+) 게시글 댓글 표시에 있던 버그 수정.

+) 슬로우 모드가 프로그램 실행 시 기본적으로 활성화 됨.

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

