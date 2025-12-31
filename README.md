# NCP Server Controller (Cloud Functions)
Naver Cloud Platform(NCP) API를 직접 호출하여 
**서버 운영 작업(기동/정지/일괄정지/정리)**과  
**백업 자동화(서버 이미지/블록스토리지 스냅샷 + 보관 정책)**,  
**비용 크레딧 조회 및 알림(메일/슬랙)**까지 한 번에 처리하는 **운영 자동화 도구**입니다.

> Cloud Functions / Scheduler / 운영 Runbook에 쉽게 붙일 수 있게 작성했습니다.

---

## Features
- **Server Control**
  - 서버 시작/정지(START/STOP)
  - 특정 서버 제외 후 전체 서버 정지(ALL_STOP_SERVER)
  - 장기간 미기동(NSTOP) 서버 자동 정리(DELETE_SERVER_INSTANCE)
  - 사용하지 않는 Public IP 정리(DELETE_PUBLICIP)
- **Backup Automation**
  - 서버 이미지 생성(CREATE_SERVER_IMAGE)
  - RUN 상태 서버를 일시 정지 후 이미지 생성 → 원상복구(FORCE_CREATE_SERVER_IMAGE)
  - OS 디스크 제외 추가 볼륨 스냅샷 생성(CREATE_SERVER_SNAPSHOT)
  - 스토리지 이름 기준 스냅샷 생성(CREATE_STORAGE_SNAPSHOT)
  - 스냅샷/이미지 **보관 정책** 지원: `count` 또는 `day`
- **Cost / Notification**
  - 잔여 크레딧 조회(CHECK_REMAINING_CREDIT) + 메일 발송
  - (옵션) 특정 액션 완료 시 Slack Webhook 알림

---

## Architecture
(Event JSON)
│
▼
Cloud Functions Handler (main.main)
│  ├─ ServerValid   : 리소스 조회/검증(서버/스토리지/PublicIP)
│  ├─ ServerControll: start/stop/정리/크레딧메일
│  ├─ ServerImage   : 서버 이미지 생성 + 보관정책
│  ├─ ServerSnapshot: 스냅샷 생성 + 보관정책
│  └─ APISender     : NCP API 인증(Signature) 생성 & 요청 전송
▼
NCP Open API (vserver / billing / mail)

---

## Supported Actions
아래 액션명은 코드에서 허용하는 목록입니다(대소문자 무관).

| Action | 설명 | 필수 파라미터 | 선택 파라미터 |
|---|---|---|---|
| GET_SERVER_INSTANCELIST | 전체 서버 목록 출력 | action | - |
| INFO_SERVER | 특정 서버 존재/ID 확인 | action, server_names | - |
| START_SERVER | 서버 시작(NSTOP → RUN) | action, server_names | - |
| STOP_SERVER | 서버 정지(RUN → NSTOP) | action, server_names | - |
| ALL_STOP_SERVER | 전체 서버 정지(예외 제외) | action | except_server_names |
| DELETE_SERVER_INSTANCE | 오래된 NSTOP 서버 정리(파괴적) | action | - |
| GET_BLOCKSTORAGE_LIST | 블록스토리지 목록 조회 | action | - |
| CREATE_SERVER_IMAGE | 정지된 서버 이미지 생성 | action, server_names, store_type, store_value | - |
| FORCE_CREATE_SERVER_IMAGE | RUN이면 정지→이미지→재기동 | action, server_names, store_type, store_value | - |
| CREATE_SERVER_SNAPSHOT | 추가 볼륨 스냅샷 생성(OS 제외) | action, server_names, store_type, store_value | - |
| CREATE_STORAGE_SNAPSHOT | 스토리지 이름 기준 스냅샷 생성 | action, storage_names, store_type, store_value | - |
| DELETE_PUBLICIP | 생성 상태 Public IP 정리(파괴적) | action | - |
| CHECK_REMAINING_CREDIT | 잔여 크레딧 조회 + 메일 발송 | action | receiveAddresses |
| CREATE_SERVER_IMAGE_SRE3 | (커스텀) 이미지 생성 + Slack 알림 | action, server_names | - |

> `store_type`: `count` 또는 `day`  
> `store_value`: 정수(1 이상)

---

## Quick Start

### 1) Requirements
- Python **3.8+** 권장 (표준 라이브러리 기반)
- NCP Open API 접근 가능한 **Access Key / Secret Key**
- (옵션) NCP Mail API 사용을 위한 설정/권한
- (옵션) Slack Incoming Webhook URL

### 2) Secrets & Config (중요)
현재 코드에는 키/웹훅이 하드코딩되어 있을 수 있습니다.  
**절대 저장소에 키를 커밋하지 마세요.** 아래 방식으로 분리하는 것을 강력 추천합니다.

- ENV 예시
  - `NCP_ACCESS_KEY`
  - `NCP_SECRET_KEY`
  - `SLACK_WEBHOOK_URL`
  - (옵션) `NCP_API_BASE_URL` (기본: `https://ncloud.apigw.ntruss.com`)
  - (옵션) `NCP_MAIL_API_BASE_URL` (기본: `https://mail.apigw.ntruss.com`)
  - (옵션) `NCP_BILLING_API_BASE_URL` (기본: `https://billingapi.apigw.ntruss.com`)

> 개선 권장: `base_auth_info.py`, `common.py`에서 환경변수를 읽도록 변경

---

## Usage (Event JSON Examples)
Cloud Functions의 `event` 입력(JSON)을 기준으로 동작합니다.

### 서버 시작
```json
{
  "action": "START_SERVER",
  "server_names": ["vm-example-01", "vm-example-02"]
}