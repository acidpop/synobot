***

### 0.14 (2022/06/15)
 - OTP Secret Key 에 잘못된 값이 입력 되는 경우 오류 수정

### 0.13 (2021/10/05)
 - OTP 자동입력 기능 추가 [설정 방법](#Otp-설정하기)

 - 로그인 풀리는 경우 자동으로 다시 로그인(ID, PW 까지는 자동 입력, 2단계 인증이 설정 되어 있고 DSM_OTP_SECRET 비밀키까지 입력이 되어 있다면 자동으로 로그인)

 - DSM 연결 실패시 실패 메시지 전송 기능 추가


### 0.12 (2021/07/10)
 - DSM 7.0 에서 OTP 로그인 안되는 오류 수정


### 0.11 (2020/10/23)
 - DSM 7.0 또는 Download Station 을 2020년 10월 20일 전후로 업데이트 한 경우 에 대한 기능 변경

 - 텔레그램으로 파일 전송시 watch_dir 로 업로드 하도록 기능 변경

 - DSM_WATCH 환경 변수 추가, Torrent Watch 경로를 마운트 한 전체 경로명 [설정 방법](#Torrent-Watch-경로-설정하기)

 - "알수 없는 에러" 알림 보내는 부분 수정


### 0.10 (2020/09/11)
 - DSM 7.0 에서 작동하지 않는 문제 수정

 - 현재 DSM 7.0 과 synobot 0.10 버전에서 토렌트 파일을 텔레그램으로 전달시 작업 등록이 되지 않는 이슈가 있습니다.

 - /task 명령 추가 (다운로드 스테이션에 작동중인 작업 목록 조회, ID, 이름, 크기, 상태, 다운로드 된 크기, 업로드 된 크기, 다운로드 속도, 업로드 속도)

 - /stat 명령 추가 (다운로드 스테이션의 네트워크 속도 정보 조회, 다운로드 속도, 업로드 속도)

### 0.9 (2020/06/02)
 - Download Station 상태 일림 메시지에서 Torrent 제목에 Markdown 문법이 포함 되는 경우 오류가 많아 Markdown 형식 삭제

### 0.8 (2020/05/22)
 - 사설 인증서 사용시 전달 받은 토렌트 파일 등록이 실패 하는 오류 수정

 - 사설 인증서 사용시 warning 로그가 계속 출력 되는 부분 수정
 
 - 작업 삭제시 삭제 된 작업 목록을 계속 가지고 있었던 오류 수정

 - TG_LANG 환경변수 추가로 로컬라이징 지원, (ko_kr, en_us), 따로 설정하지 않으면 ko_kr 로 작동

### 0.7 (2020/05/19)
 - DSM_AUTO_DEL 환경 변수 추가, 기본값은 0이며 작업 완료시 자동 삭제가 필요하면 1 로 변경해서 사용

 - Download Station 자동 삭제 기능 추가

### 0.6 (2020/05/18)
 - DSM_PW 환경 변수가 없는 경우 Docker 가 시작 하지 못 하는 오류 수정

 - 텔레그램 봇에 /dslogin 명령 추가 (재 로그인 시도 명령)

 - 2단계 인증 지원 (OTP)

 - 로그인 코드 전체 변경

 - DSM_CERT 환경 변수 추가 (https 사용시 인증서 불일치인 경우 해당 값을 0으로 변경 해서 사용)

### 0.5 (2019/09/03)
 - DS Download 알림 시 Markdown 문법 제거

 - LOG 관련 환경 변수 제거

### 0.4 (2019/08/30)
 - Torrent 제목에 [] 중괄호가 포함 되어 있는 경우 오류 수정

 - 다운로드 중 삭제시 오류 케이스 수정

### 0.3
 - 언어팩 관련 준비 (SYNO_LANG 환경 설정에 따라 언어팩 로딩)

 - 다운로드 취소시 중복 메시지 발생 오류 수정

### 0.2
 - request 예외 처리

### 0.1

 - synobot 최초 버전

***

# Synology DSM Download Station Task Monitor and Create Task Magnet, Torrent File

## **synobot 기능**

synobot 은 다음과 같이 간단한 기능만 제공 합니다.

1. Download Station 작업 목록 Telegram 알림,
  - 알림 기준
    - 최초 작업 등록 후 받을 사이즈가 0이상인 경우
    - 상태 값이 바뀌는 경우 (다운로드중 -> 완료)
    - 작업 목록이 삭제 되는 경우

2. Magnet 링크 지원
  - Telegram BOT 에 magnet 링크를 보내면 Download Station 에 등록 합니다.

3. Torrent 파일 지원
  - Telegram BOT 에 Torrent 파일을 전송 하면 Download Station 에 등록 합니다.

4. /dslogin 명령 지원
  - Telegram BOT 에 /dslogin 커맨드를 전송 하면 로그인을 재시도 합니다.
                        

## **도커 설치시 환경 변수에 다음 값을 설정 해야 합니다.**

텔레그램 알람을 받을 사용자 chat id (여러명을 사용해야 하는 경우 ,콤마로 구분되며 공백이 없어야 합니다)

**TG_NOTY_ID** *12345678,87654321*

텔레그램 봇 토큰을 입력합니다

**TG_BOT_TOKEN** *186547547:AAEXOA9ld1tlsJXvEVBt4MZYq3bHA1EsJow*

텔레그램 봇 명령 사용시 허용 할 사용자의 chat id, 여러명 허용시 ,콤마로 구분되며 공백이 없어야 합니다

**TG_VALID_USER** *12345678,87654321*

DSM 로그인 할 사용자 ID를 입력합니다.

**DSM_ID** *your_dsm_id*

DSM 에 로그인 할 ID 를 입력합니다

**TG_DSM_PW_ID** *12345678*

Download Station 에 로그인시 암호를 물어 볼 Telegram 사용자의 chat id를 입력합니다.

**DSM_URL** *https://DSM_IP_OR_URL*

DSM URL, http 또는 https 까지 모두 포함하여 입력하고 포트는 제외해야 합니다

예시) 올바른 예 - https://www.dsm.com

잘못 된 예 - https://www.dsm.com:8000

**DS_PORT** *8000*

DSM 제어판 -> 응용 프로그램 포털 -> Download Station 의 포트를 입력합니다.

DSM_URL 에 입력한 http 또는 https 에 맞춰서 입력하셔야 합니다.

**SYNO_LANG** *ko_kr*

synobot 언어팩 설정입니다. 현재 버전에는 ko_kr 버전만 지원 합니다.

**DSM_CERT** *1*

DSM_URL 에 https 사용시 DSM 인증서가 도메인과 일치하지 않는 경우에 사설 인증서를 사용 가능하도록 하는 환경 변수입니다.

사설 인증서를 사용 한다면 값을 0 으로 사용하시면 됩니다.

**DSM_OTP_SECRET** "VFGW"

DSM 2단계 인증 설정시 비밀 키의 값을 입력

[설정 방법](#Otp-설정하기)

**TZ** *Asia/Seoul*

Synobot 도커가 작동하는 지역의 시간대 설정

링크(https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) 의 *TZ database name* 에 해당 하는 값을 사용

**DOCKER_LOG**

Synobot 도커의 로그를 컨테이너 상세보기의 로그 탭에서 확인 할 수 있도록 설정

1 : 컨테이너 로그 화면에서 확인 가능

0 : 도커 내부의 로그 파일에만 기록

***

**DSM_PW 환경 변수가 없는 경우에는 synobot 도커가 재시작 될 때마다 텔레그램 봇이 DSM 로그인 암호를 요청합니다.**

**synobot 은 사용자 암호를 어느곳에도 저장하지 않습니다.**

**텔레그램 봇으로 전달 받은 암호 메시지는 수신 즉시 봇이 삭제 합니다.**

매번 암호 입력하는것이 번거러운 경우 DSM_PW 환경 변수에 DSM 로그인 암호를 추가 하면 해당 암호를 이용하여 DSM 에 로그인합니다.

DSM_PW 환경 변수를 + 버튼을 클릭하여 직접 입력해주셔야 합니다

**DSM_PW** *your_dsm_password*

***


Synology Docker 에서 다음과 같이 화면에서 세팅하면 됩니다.

![synobot_config_1](https://raw.githubusercontent.com/acidpop/synobot_public/master/img/synobot_config1.png)

![synobot_config_2](https://raw.githubusercontent.com/acidpop/synobot_public/master/img/synobot_config2.png)

![synobot_config_3](https://raw.githubusercontent.com/acidpop/synobot_public/master/img/synobot_config3.png)

***

- Tip

Telegram 사용자의 chat id 알아내기

<a href="https://blog.acidpop.kr/216?category=679730" target="_blank">chat id 알아내기</a>

***

synobot 안내 문구 커스터마이징 하기

1. DSM 의 터미널에 접속 한 후 sudo -i 명령으로 root 권한으로 로그인.

2. docker ps -a 명령으로 현재 실행 되어 있는 synobot의 Container ID 값을 알아낸다.

3. docker exec -it {Container ID} /bin/bash  명령으로 Docker 내부에 접속한다.

4. apt-get update

5. apt-get install vim

6. vim 으로 ko_kr.json 파일을 열어 문구를 알맞게 수정 한다.

7. synobot 도커 재시작

***


## Torrent Watch 경로 설정하기

0.11 버전에서 신규 추가 된 DSM_WATCH 환경 변수를 설정 하는 방법은 다음과 같다.

1. 고급 설정 버튼 클릭

![synobot_config_4](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config4.png)

2. 볼륨 탭 선택 후 폴더 추가 버튼 클릭

![synobot_config_5](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config5.png)

3. Download Station 에서 설정한 watch 경로를 선택

![synobot_config_6](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config6.png)

4. 마운트 경로 부분에 **/tor_watch** 입력

![synobot_config_7](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config7.png)

5. 환경 변수 설정 탭에서 DSM_WATCH 변수의 값에 **/tor_watch** 입력

![synobot_config_8](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config8.png)


## #Otp 설정하기

0.13 버전에서 신규 추가 된 OTP 자동 입력 기능 설정 방법은 다음과 같다.

1. 게정 설정에서 2단계 인증 추가를 클릭한다.

2. QR 코드 스캔 화면이 나오면 "스캔 할 수 없습니까" 를 클릭한다.

![synobot_config_9](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config9.png)

3. 비밀 키에 해당 하는 값을 기록 해 둔다.

![synobot_config_10](https://raw.githubusercontent.com/acidpop/synobot/master/img/synobot_config10.png)

4. Synobot 의 Docker 세팅시 DSM_OTP_SECRET 환경 변수에 해당 비밀키를 입력한다.

----

문의 사항은 github synobot Repository 를 이용해 주세요

<a href="https://github.com/acidpop/synobot_public" target="_blank">synobot github</a>



