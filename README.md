
# Blue_Dump
---
## 📄 목차
[🐶 프로젝트 개요](#-프로젝트-개요)   
[🔍 프로젝트 소개](#-프로젝트-소개)   
[💻 개발 환경](#-개발-환경)   
[📌 주요 기능](#-주요-기능)   
[📱 페이지별 기능](#-페이지별-기능)


### 🐶 프로젝트 개요
---
- 프로젝트 이름 : 3조핑
- 프로젝트 기간 : 24/10/07~
- 멤버 : 허욱(팀장), 강효빈, 송현규, 오동석, 양혜선


### 🔍 프로젝트 소개
---
- **Blue Dump**는 인공지능(AI)을 이용해 인물별로 사진을 분류하고 공유하는 안드로이드 어플입니다.
- **Blue Dump**를 통해 더 편리한 사진 공유를 함으로써 사진을 공유할 때 인물들을 한명씩 구별하여 선택해서 보내야 하는 번거로움을 줄여줄 수 있습니다.


### 💻 개발 환경
---
**1. Front-end**
- Framework and Language :  
  <img src="https://img.shields.io/badge/Kotlin-7F52FF?style=for-the-badge&logo=Kotlin&logoColor=white"> <img src="https://img.shields.io/badge/MVVMRepository-FED12F?style=for-the-badge&logo=MVVMRepository&logoColor=white">
  <img src="https://img.shields.io/badge/Retrofit-FE5F50?style=for-the-badge&logo=retrofit&logoColor=white"> <img src="https://img.shields.io/badge/coroutine-222222?style=for-the-badge&logo=coroutine&logoColor=white"> <img src="https://img.shields.io/badge/di-008FC7?style=for-the-badge&logo=di&logoColor=white"> <img src="https://img.shields.io/badge/compose-FF0000?style=for-the-badge&logo=compose&logoColor=white"> <img src="https://img.shields.io/badge/flow-8BC0D0?style=for-the-badge&logo=flow&logoColor=white">


**2. Back-end**
- Framework and Language :  
  ![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white) <img src="https://img.shields.io/badge/springboot-2496ED?style=for-the-badge&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/Spring Security-6DB33F?style=for-the-badge&logo=Spring Security&logoColor=white"> <img src="https://img.shields.io/badge/Spring data JPA-EC1C24?style=for-the-badge&logo=springdatajpa&logoColor=white">
- Database : <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white"> <img src="https://img.shields.io/badge/JPA-ECD53F?style=for-the-badge&logo=jpa&logoColor=white"> <img src="https://img.shields.io/badge/Hibernate-59666C?style=for-the-badge&logo=Hibernate&logoColor=white">

- Security and Certification : <img src="https://img.shields.io/badge/Spring Security-6DB33F?style=for-the-badge&logo=Spring Security&logoColor=white">  <img src="https://img.shields.io/badge/OAuth2-EB5424?style=for-the-badge&logo=r=white">
- Build : <img src="https://img.shields.io/badge/Gradle-02303A?style=for-the-badge&logo=Spring&logoColor=white">
- Other Libraries :  
  <img src="https://img.shields.io/badge/Lombok-4285F4?style=for-the-badge&logo=lombok&logoColor=white"> <img src="https://img.shields.io/badge/Jakarta Servlet-B6A272?style=for-the-badge&logo=jakartaservlet&logoColor=white"> <img src="https://img.shields.io/badge/Tomcat Embed Jasper-F1007E?style=for-the-badge&logo=tomcatembedjasper&logoColor=white">

**3. AI**
- Framework and Language :   
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) <img src="https://img.shields.io/badge/DeepFace-9266CC?style=for-the-badge&logo=deepface&logoColor=white"> ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)

**4. Service Deployment Environment** : <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white">

**5. Design**  : ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) <img src="https://img.shields.io/badge/drawio-ECD53F?style=for-the-badge&logo=white"> <img src="https://img.shields.io/badge/DBdiagram.io-F08705?style=for-the-badge&logo=dbdiagram&logoColor=white">

**6. Communication** : 	<img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"> <img src="https://img.shields.io/badge/notion-000000?style=for-the-badge&logo=notion&logoColor=white">



### 📌 주요 기능
---
**1. 자동 얼굴 인식 및 분류**  
AI 모델이 여러 장의 사진에서 얼굴을 인식하고, 인물별로 사진을 분류합니다.


**2. 개인별 사진 열람**  
사용자는 어플을 통해 자신이 포함된 사진만 볼 수 있는 폴더를 제공받습니다.

**3. 사진 다운로드 및 공유**  
사용자는 분류된 사진을 다운로드하거나, 원하는 사진을 친구와 공유할 수 있습니다.

**4. 사진 저장 기능**  
이용했던 서비스의 사진들을 보관할 수 있습니다.

**5.  보안 및 접근 권한 관리**  
사진에 접근할 수 있는 사람을 자동으로 설정하여, 불필요한 접근을 차단하고 개인 정보를 보호합니다.




### 📱 페이지별 기능
---
**[초기화면] - FE**

<img width="162.56px" height="337.92px" alt="스플래쉬 화면" src="https://github.com/user-attachments/assets/5e1ab6ab-d78c-4876-9db6-7db362c6ae27">

-  초기화면으로 'Blue Dump' 스플래시 화면 후 페이지 전환됩니다.
    -  회원가입 O : 아이디와 비밀번호 입력 페이지가 나타납니다.
    -  회원가입 X : 회원가입 버튼 -> 회원가입 페이지가 나타납니다.

</p>   

**[로그인] - BE**


<img width="162.56px" height="337.92px" alt="로그인 화면" src="https://github.com/user-attachments/assets/4c70de04-e901-4078-8952-71afdb9797b0">
<img width="162.56px" height="337.92px" alt="아이디 미입력 오류" src="https://github.com/user-attachments/assets/44b7034b-9e91-47ee-9a64-0950dc13f372">
<img width="162.56px" height="337.92px" alt="비밀번호 미입력 오류" src="https://github.com/user-attachments/assets/1b2a4640-a4c1-4ee4-90f6-fdd8d37b08d1">
<img width= "162.56px" height="337.92px" alt="아이디, 비밀번호 불일치 오류" src="https://github.com/user-attachments/assets/6fa96796-8a42-45ef-8c68-4e0270852734">

-  ID를 입력하지 않고 로그인 버튼을 클릭 ->  $\rm{\small{\color{#DD6565}'!ID를\ 입력해주세요'}}$라는 메시지가 나타납니다.
-  패스워드를 입력하지 않고 로그인 버튼을 클릭 ->  $\rm{\small{\color{#DD6565}'!패스워드를\ 입력해주세요'}}$ 라는 메시지가 나타납니다.
-  부정확한 아이디나 패스워드를 입력하고 로그인 버튼을 클릭 -> $\rm{\small{\color{#DD6565}'!ID와\ 패스워드를\ 확인해주세요'}}$라는 메시지가 나타납니다.
-  로그인 성공 시 홈 화면으로 이동합니다.


**[회원가입] - FE**

<img width="162.56px" height="337.92px" alt="회원가입 화면 Ver 2" src="https://github.com/user-attachments/assets/c1e68945-eb06-4dac-8c0b-a48cde8478c5">
<img width="162.56px" height="337.92px" alt="프로필 이미지 업로드" src="https://github.com/user-attachments/assets/63d004ad-1a45-421f-ad61-647fbb89cfd1">
<img width="162.56px" height="337.92px" alt="사진 2개 선택 오류 (1)" src="https://github.com/user-attachments/assets/ee6fff2c-bd09-4710-967d-ec4b4e7e3953">
<img width="162.56px" height="337.92px" alt="중복 ID 오류" src="https://github.com/user-attachments/assets/16995cbc-559c-48a3-b969-43d666343cb9">
<img width="162.56px" height="337.92px" alt="중복 PW 오류" src="https://github.com/user-attachments/assets/23e6106f-c0d4-4ee2-8430-aa599beb14aa">


-  프로필 사진 등록 시 사용자의 드라이브나 갤러리 앱에서 사진을 등록합니다. **1장**만 선택 가능합니다.
-  회원  닉네임을 지정할 수 있습니다.
-  아이디는 영문, 숫자 조합 **8-12자** 입력 가능합니다.
-  비밀번호는 영문, 숫자 조합 **8-12자** 입력 가능하고, 오입력 방지를 위해 **2회** 입력합니다.
-  존재하는 아이디, 비밀번호를 입력할 경우 $\rm{\small{\color{#DD6565}'!다른\ 아이디,\ 비밀번호를\ 입력해주세요'}}$ 의 메시지가 나타납니다.
-  비밀번호가 다를 경우 $\rm{\small{\color{#DD6565}'!비밀번호가\ 일치하지\ 않습니다'}}$ 의 메시지가 나타납니다.


**[마이페이지] - FE**

<img width="162.56px" height="337.92px" alt="그룹방 보기" src="https://github.com/user-attachments/assets/b011c9c4-02e7-445a-83a5-770b69c81b42">
<img width="162.56px" height="337.92px" alt="그룹방목록" src="https://github.com/user-attachments/assets/93314bbb-b1aa-40c6-964e-616c71a5896a">

-  로그인 후 처음으로 노출되는 페이지입니다.
-  오른쪽 하단의 **+** 버튼을 누르면 그룹방을 생성할 수 있습니다.
-  마이페이지 화면에는 자신이 속한 그룹방 목록이 나타납니다.

**[그룹방생성] - BE**

<img width="162.56px" height="337.92px" alt="그룹방 생성" src="https://github.com/user-attachments/assets/8da8cdc3-019f-4220-abf9-34c65ae9728b">

-  그룹방 이름을 설정할 수 있습니다.
-  '사진 미리 공유' 또는 '개인적 모임 후 사람들과 보기' 옵션을 선택할 수 있으며 미선택시 '사진 미리 공유'로 설정됩니다.
-  완료 버튼을 누르면 그룹방이 생성됩니다.
-  그룹방 입장 버튼이 나타납니다.

**[그룹방]**

**1. 그룹방 링크 복사 - FE**

<img width="162.56px" height="337.92px" alt="그룹방 사이드 패널" src="https://github.com/user-attachments/assets/ca1ebfa9-3fdc-4e3f-a115-a859670309d8">

-  오른쪽 상단의 사이드바를 클릭하면 복사 가능한 **'그룹방 링크'** 가 존재하고 그 아래로는 참여하는 그룹 멤버들의 닉네임이 나타납니다.
-  링크를 받은 참여자들은 링크를 클릭하면 어플을 다운받을 수 있고, 회원가입이나 로그인 화면으로 넘어가게 됩니다.

**2. 사진업로드 - FE**

<img width="162.56px" height="337.92px" alt="그룹방 화면" src="https://github.com/user-attachments/assets/71683579-f3c6-4953-956f-89a7edeb9424">
<img width="162.56px" height="337.92px" alt="사진 업로드 _ 갤러리 접근 화면" src="https://github.com/user-attachments/assets/b39f66e7-90a5-40b0-945e-4c51c6f4100b">

-  페이지 하단에 '사진업로드' 버튼이 활성화됩니다.
-  사진 업로드 버튼 클릭시 안드로이드 스마트폰의 갤러리 앱이 열리며, 업로드를 원하는 사진들을 체크하여 선택할 수 있습니다.

**3. AI 분류하기 - AI**

<img width="162.56px" height="337.92px" alt="ai분류하기활성화" src="https://github.com/user-attachments/assets/0b547be9-2b27-478d-bed6-300981f02180">
<img width="162.56px" height="337.92px" alt="AI 회원별 분류되는 중" src="https://github.com/user-attachments/assets/37267cab-0880-4533-8ad7-9fb1a3a69c59">

-  방장에게는 마이페이지 화면에 **'AI 분류하기'** 버튼이 나타납니다.
-  **'AI 분류하기'** 버튼은 사진 한 장이라도 업로드 시 활성화됩니다.
-  AI가 사람얼굴이 포함되지 않은 사진으로 판별했을 경우 기타 사진으로 분류합니다.
-  그룹방 상태는 **'기본', '분류중', '분류완료'** 로 나뉩니다.


**4. 사진 분류완료 - BE, AI**

<img width= "162.56px" height="337.92px" alt="분류 완료_전체 공유_ver 2 (1)" src="https://github.com/user-attachments/assets/3d122fdf-0053-4fe3-aadc-624b95598fbb">
<img width="162.56px" height="337.92px" alt="분류 완료_부분 공유_ver 2" src="https://github.com/user-attachments/assets/dc8ce49c-1e42-42a3-b58f-3db0c6580f7f">

- 분류가 완료되면 자동으로 그룹방 페이지로 진입합니다.
-  그룹방 페이지 내에 인물별 사진폴더가 생성됩니다.
    - '사진 미리 공유' 를 선택한 그룹방 :  모든 멤버들의 사진폴더들이 나타납니다.
    - '개인적 모임 후 사람들과 보기'를 선택한 그룹방 : 각자의 사진이 포함된 폴더만 나타납니다.
-  멤버별 사진 분류 결과대로 각 회원에게 사진 다운로드를 위한 페이지가 제공됩니다.
