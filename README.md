# ThanosCleaner (디시클리너)

## ThanosCleaner란?
한 번의 핑거 스냅으로 우주의 절반을 소멸시킨 타노스를 본받아 한 번의 클릭으로

당신의 디시인사이드 게시글/댓글/스크랩/방명록을 삭제해주는 디시인사이드 클리너입니다.

## ThanosCleaner의 사용법은?
[여기](https://github.com/augustapple/ThanosCleaner/releases)를 클릭하여 미리 패키징된 파일을 다운로드 하거나

아래의 명령어로 직접 패키징하여 사용할 수 있습니다.

```
pyinstaller -F -w --icon="dependencies/image/Thanos.ico" ThanosCleaner.py
```

프로그램을 실행하면 아래와 같은 화면이 나옵니다.

![UI](https://user-images.githubusercontent.com/57178921/68082112-f8bb1500-fe5b-11e9-9f62-474edc41381a.PNG)

해당 화면에 아이디와 비밀번호를 입력하고 엔터 혹은 로그인 버튼을 눌러 로그인을 합니다.

아래와 같이 로그인이 완료되었을 경우, 게시글/댓글/스크랩/방명록 삭제 버튼을 눌러 삭제를 시작합니다.

![loginUI](https://user-images.githubusercontent.com/57178921/68082111-f8bb1500-fe5b-11e9-991d-42999fe07700.PNG)

로그아웃은 언제든 가능하며, 삭제가 진행중일 경우 로그아웃을 하기 전 유저에게 확인을 묻습니다.

## Special Thanks

베타버전을 테스트해준 ㄴㅁㅈㄱ, 대리영정, 플링츄, 배교자 님

제작하신 클리너의 코드 비상업적 사용을 허가해주신 [logs3](https://github.com/logs3) 님

이슈를 제보해주신 [craftingmod](https://github.com/craftingmod) 님

스크랩, 방명록 삭제 기능을 추가해주신 [L4by](https://github.com/L4by) 님

ThanosCleaner를 직접 검수해주신 [티바이트](https://github.com/tibyte) 님

ThanosCleaner의 구조를 짜는데 도와주신 [쪼리핑](https://github.com/JJoriping) 님

## 오류가 발생했을 시
해당 리포지토리의 [Issues](https://github.com/augustapple/ThanosCleaner/issues)에 작성해주시거나

augustapple77@gmail.com 으로 보내주시면 됩니다.

클리너를 다운로드 받으신 폴더 내에 thanoscleaner.log 파일을 동봉해주시면 원인 파악에 큰 도움이 되니

꼭!! 함께 보내주시기 바랍니다. 감사합니다.
