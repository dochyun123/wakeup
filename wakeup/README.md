# Wakeup QR Check Project

QR 코드 체크 시스템 - 로컬 CSV 또는 Google Spreadsheet를 사용하여 QR 데이터를 관리할 수 있습니다.

## 📋 목차
- [기능](#기능)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [설정 파일](#설정-파일)
- [문제 해결](#문제-해결)
- [Apps script](#기능-사용방법)

## ✨ 기능

- **로컬 CSV 파일 사용**: 오프라인에서 QR 데이터 관리
- **Google Spreadsheet 연동**: 실시간 데이터 동기화 및 협업
- 두 가지 방식 모두 지원하여 유연한 사용 가능

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/dochyun123/wakeup.git
cd wakeup
```

### 2. 의존성 패키지 설치

**conda 환경 사용 (권장)**
```bash
conda env create -n wakeup
conda activate wakeup
```

**pip 사용**
```bash
pip install -r requirements.txt
```

## 📖 사용 방법

### Option 1: 로컬 CSV 파일 사용

로컬에 저장된 CSV 파일로 QR 코드를 체크합니다.

```bash
python checkQR.py
```

**필요사항:**
- CSV 파일이 프로젝트 폴더에 준비되어 있어야 합니다.

---

### Option 2: Google Spreadsheet 사용

Google Spreadsheet와 연동하여 실시간으로 데이터를 관리합니다.

```bash
python QRgspread.py
```

**사전 준비:**

#### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. **Google Sheets API** 활성화
4. 서비스 계정 생성:
   - IAM 및 관리자 > 서비스 계정 > 서비스 계정 만들기
   - 역할: 편집자 또는 소유자
5. JSON 키 다운로드
   - 생성된 서비스 계정 > 키 > 키 추가 > JSON

#### 2. 설정 파일 생성


**실제 값 입력:**
- `sheetUrl`: Google Spreadsheet의 전체 URL
- `sheetName`: Google Spreadsheet 이름
  ```
  https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit
  ```
- `jsonKeyFilePath`: 다운로드한 JSON 키 파일의 경로

#### 3. Spreadsheet 공유 설정
다운로드한 JSON 파일에서 `client_email` 값을 확인하고, 해당 이메일 주소에 Spreadsheet 편집 권한을 부여하세요.

```json
{
  "client_email": "your-service-account@project-id.iam.gserviceaccount.com",
  ...
}
```

## 📁 프로젝트 구조

```
wakeup/
├── checkQR.py              # 로컬 CSV 사용
├── QRgspread.py            # Google Spreadsheet 사용
├── requirements.txt        # Python 패키지 목록
└── README.md              # 프로젝트 문서
```

## 🔧 문제 해결

### Google Sheets API 오류
```
gspread.exceptions.APIError: [403]
```
**해결 방법:**
1. Google Sheets API가 활성화되어 있는지 확인
2. 서비스 계정 이메일에 Spreadsheet 공유 권한이 있는지 확인
3. JSON 키 파일 경로가 올바른지 확인

# 🔗 Google Apps Script 연동

Google Spreadsheet에서 자동으로 QR 코드를 생성하고 문자 메시지를 전송하는 기능입니다.

### 기능
- **고유번호 자동 생성**: 응답이 기록될 때마다 고유 ID 생성
- **QR URL 자동 생성**: 생성된 고유번호로 QR 코드 URL 생성
- **문자 메시지 자동 전송**: QR 코드 정보를 SMS로 전송

#### 1. Apps Script 에디터 열기
1. Google Spreadsheet 열기
2. 상단 메뉴: **확장 프로그램** > **Apps Script** 클릭
3. 새 Apps Script 프로젝트가 열립니다

#### 2. 코드 작성
1. 기본 생성된 `Code.gs` 파일 내용을 모두 삭제
2. 프로젝트 내 `appscript.js` 파일 내용을 복사
3. Apps Script 에디터에 붙여넣기
4. 💾 **저장** (Ctrl + S 또는 저장 아이콘 클릭)

#### 3. 트리거 설정
1. 좌측 메뉴에서 **⏰ 트리거** (시계 아이콘) 클릭
2. 우측 하단 **+ 트리거 추가** 클릭
3. 다음과 같이 설정:
   - **실행할 함수 선택**: `onFormSubmit` (또는 코드의 메인 함수명)
   - **이벤트 소스 선택**: 스프레드시트에서
   - **이벤트 유형 선택**: 양식 제출 시
4. **저장** 클릭
5. Google 계정 권한 승인
