# ThanosCleaner (디시클리너)

## ThanosCleaner란?
한 번의 핑거 스냅으로 우주의 절반을 소멸시킨 타노스를 본받아 한 번의 클릭으로

당신의 디시인사이드 게시글/댓글을 삭제해주는 디시인사이드 클리너입니다.

## ThanosCleaner의 사용법은?
[여기](https://github.com/augustapple/ThanosCleaner/releases/tag/v1.0)를 클릭하여 미리 패키징된 파일을 다운로드 하거나

아래의 명령어로 직접 패키징하여 사용할 수 있습니다.

```
pyinstaller -F -w --icon="dependencies/image/Thanos.ico" ThanosCleaner.py
```

프로그램을 실행하면 아래와 같은 화면이 나옵니다.

![UI](https://user-images.githubusercontent.com/57178921/67903827-f7fe5680-fbaf-11e9-85de-fcbcbfc5cefe.PNG)

해당 화면에 아이디와 비밀번호를 입력하고 엔터 혹은 로그인 버튼을 눌러 로그인을 합니다.

아래와 같이 로그인이 완료되었을 경우, 게시글/댓글 삭제 버튼을 눌러 삭제를 시작합니다.

![loginUI](https://user-images.githubusercontent.com/57178921/67903828-f7fe5680-fbaf-11e9-878b-4e1dfb4b95ae.PNG)

로그아웃은 언제든 가능하며, 삭제가 진행중일 경우 로그아웃을 하기 전 유저에게 확인을 묻습니다.

## Special Thanks
베타버전을 테스트해준 ㄴㅁㅈㄱ, 대리영정, 플링츄, 배교자 님

ThanosCleaner를 직접 검수해주신 [티바이트](https://github.com/tibyte) 님

ThanosCleaner의 구조를 짜는데 도와주신 [쪼리핑](https://github.com/JJoriping) 님

## 오류가 발생했을 시
해당 리포지토리의 [Issues](https://github.com/augustapple/ThanosCleaner/issues)에 작성해주시거나

augustapple77@gmail.com 으로 보내주시면 됩니다.
