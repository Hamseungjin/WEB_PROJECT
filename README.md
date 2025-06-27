# 🎵 SOTP (SHOUT OUT TO SPOTIFY)
**AI 기반 음악 추천 웹 서비스**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3.0-red.svg)](https://pytorch.org)
[![Transformers](https://img.shields.io/badge/🤗%20Transformers-4.50.0+-yellow.svg)](https://huggingface.co/transformers/)

## 📖 프로젝트 소개

SOTP는 **Spotify API**와 **Google Gemma-3-4b-it** AI 모델을 활용한 지능형 음악 추천 웹 서비스입니다. 사용자의 음악 취향을 분석하고 개인화된 추천을 제공하며, 자연스러운 한국어 대화가 가능한 음악 전문 AI 챗봇을 포함하고 있습니다.

### ✨ 주요 기능

#### 🎧 음악 서비스
- **개인화된 음악 추천**: Multi-Armed Bandit 알고리즘 기반
- **Spotify 연동**: 플레이리스트, 상위 트랙, 아티스트 정보
- **글로벌 & 국내 트렌드**: 실시간 차트 정보
- **리뷰 시스템**: 사용자 음악 리뷰 및 평점

#### 🤖 AI 챗봇 (NEW!)
- **Gemma-3-4b-it 모델**: Google의 최신 대화형 AI
- **음악 전문 지식**: 아티스트, 장르, 트렌드 정보 제공
- **맥락 인식 대화**: 이전 대화 기억 및 연속성 유지
- **자연스러운 한국어**: 친근하고 전문적인 응답

#### 🗄️ 데이터 관리
- **MongoDB**: 사용자 데이터 및 음악 정보 저장
- **실시간 동기화**: Spotify API와 데이터베이스 연동
- **Docker 지원**: 컨테이너화된 배포

---

## 🚀 빠른 시작

### 📋 사전 요구사항

- **Python 3.8+**
- **Docker & Docker Compose** (권장)
- **CUDA 호환 GPU** (선택사항, AI 모델 가속용)
- **Spotify Developer Account** (필수)

### 🔑 Spotify API 설정

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에서 앱 생성
2. **Client ID**, **Client Secret** 획득
3. **Redirect URI** 설정: `https://127.0.0.1:5000/callback`

### 📦 설치 방법

#### 방법 1: Docker 사용 (권장)

```bash
# 저장소 클론
git clone <repository-url>
cd WEB_PROJECT

# 환경 변수 설정
export client_id="your_spotify_client_id"
export client_secret="your_spotify_client_secret"
export secret_key="your_flask_secret_key"

# Docker Compose로 실행
docker-compose up --build
```

#### 방법 2: 로컬 설치

```bash
# 저장소 클론
git clone <repository-url>
cd WEB_PROJECT

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirement.txt

# MongoDB 실행 (별도 터미널)
mongod

# 환경 변수 설정
export client_id="your_spotify_client_id"
export client_secret="your_spotify_client_secret"
export secret_key="your_flask_secret_key"

# 애플리케이션 실행
python app.py
```

### 🌐 접속

- **웹 서비스**: `https://127.0.0.1:5000`
- **챗봇 테스트**: `python chat.py` (터미널에서 직접 테스트)

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   External      │
│                 │    │                  │    │                 │
│ • HTML/CSS/JS   │◄──►│ • Flask Routes   │◄──►│ • Spotify API   │
│ • Bootstrap UI  │    │ • Session Mgmt   │    │ • Gemma-3-4b-it │
│ • Chat Interface│    │ • API Endpoints  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │    Database      │
                       │                  │
                       │ • MongoDB        │
                       │ • User Data      │
                       │ • Music Info     │
                       │ • Reviews        │
                       └──────────────────┘
```

---

## 🤖 AI 챗봇 사용법

### 💬 기본 대화
```
사용자: 안녕하세요!
SOTP: 안녕하세요! SOTP 음악 서비스에 오신 걸 환영해요. 어떤 음악에 대해 궁금한 점이 있으신가요?

사용자: 요즘 트렌드가 뭐예요?
SOTP: 현재 글로벌 차트에서는 Taylor Swift의 새 앨범이 큰 인기를 끌고 있고, K-pop에서는 NewJeans와 aespa가 상위권을 차지하고 있어요...
```

### 🎵 음악 추천
```
사용자: 차분한 음악 추천해주세요
SOTP: 차분한 음악을 좋아하시는군요! 어떤 장르를 선호하시나요? 
- 어쿠스틱 팝 (에드 시런, 존 메이어)
- 재즈 (노라 존스, 빌 에반스)
- 인디 포크 (봉봉, 잔나비)
중에서 선택하시거나 다른 스타일도 말씀해주세요!
```

### 🔧 챗봇 관리 API

```bash
# 챗봇 상태 확인
curl https://127.0.0.1:5000/chat/status

# 대화 기록 초기화
curl -X POST https://127.0.0.1:5000/chat/clear
```

---

## 📊 주요 기능 상세

### 🎯 음악 추천 알고리즘

**Multi-Armed Bandit (MAB) 알고리즘** 사용:
- **Cold Start Problem 해결**: 신규 사용자도 즉시 추천 가능
- **동적 학습**: 사용자 반응에 따른 실시간 알고리즘 조정
- **탐색과 활용 균형**: 새로운 음악 발견과 기존 취향 만족

### 🗃️ 데이터베이스 구조

#### 컬렉션 목록
```
user_spotify_info/
├── playlists              # 사용자 플레이리스트
├── most_listened_songs    # 최다 청취곡
└── top_artists           # 상위 아티스트

recommendation_info/
├── recommendations       # 추천 음악
├── top_tracks           # 글로벌 인기곡
├── kr_top_tracks        # 국내 인기곡
└── global_latest_tracks # 최신 트렌드

review_info/
└── review               # 사용자 리뷰
```

### 🔐 보안 & 인증

- **OAuth 2.0**: Spotify 계정 연동
- **세션 관리**: Flask 세션 기반 인증
- **토큰 갱신**: 자동 액세스 토큰 리프레시
- **권한 관리**: 관리자/일반 사용자 구분

---

## 🛠️ 개발 정보

### 📁 프로젝트 구조

```
WEB_PROJECT/
├── app.py                 # Flask 메인 애플리케이션
├── chat.py               # Gemma-3-4b-it 챗봇 (NEW!)
├── requirement.txt       # Python 의존성
├── docker-compose.yml    # Docker 설정
├── Dockerfile           # 컨테이너 이미지
├── static/              # 정적 파일 (CSS, JS, 이미지)
├── templates/           # HTML 템플릿
└── Doc_img/            # 문서 이미지
```

### 🔄 개발 워크플로우

1. **사용자 인증**: Spotify OAuth → 세션 생성
2. **데이터 수집**: Spotify API → MongoDB 저장
3. **추천 생성**: MAB 알고리즘 → 개인화된 결과
4. **AI 대화**: Gemma-3-4b-it → 자연어 응답
5. **결과 표시**: Flask 템플릿 → 사용자 인터페이스

### 🧪 테스트

```bash
# 챗봇 단독 테스트
python chat.py

# API 테스트
curl -X POST https://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!"}'

# Spotify API 연동 테스트
https://127.0.0.1:5000/test
```

---

## 🚨 문제 해결

### 일반적인 문제들

**1. 모델 로딩 실패**
```bash
# GPU 메모리 부족시
export CUDA_VISIBLE_DEVICES=""  # CPU만 사용
```

**2. Spotify API 오류**
```bash
# 토큰 만료시 자동 갱신 확인
https://127.0.0.1:5000/refresh-token
```

**3. MongoDB 연결 오류**
```bash
# Docker 환경에서
docker-compose restart mongodb

# 로컬 환경에서
mongod --repair
```

### 🔍 디버깅

```bash
# 애플리케이션 로그 확인
docker-compose logs -f app

# 챗봇 상태 확인
curl https://127.0.0.1:5000/chat/status
```

---

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

## 👥 팀 정보

**팀명**: GOAT  
**작성일**: 2024/05/27 (최종 업데이트: 2024/12/19)

### 🔗 관련 링크

- [Spotify Developer Documentation](https://developer.spotify.com/documentation/)
- [Gemma-3-4b-it Model](https://huggingface.co/google/gemma-3-4b-it)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## 🆕 최근 업데이트 (v2.0)

### ✅ 새로운 기능
- **Gemma-3-4b-it AI 모델** 통합으로 고급 대화형 챗봇 구현
- **맥락 인식 대화** 및 음악 전문 지식 제공
- **개선된 API 엔드포인트** (`/chat/status`, `/chat/clear`)
- **향상된 오류 처리** 및 대체 응답 시스템

### 🔄 변경사항
- 기존 간단한 패턴 매칭 챗봇 → 고급 AI 모델로 교체
- `transformers` 및 `accelerate` 라이브러리 추가
- 더 자연스럽고 유용한 음악 관련 대화 지원

**SOTP와 함께 새로운 음악 여행을 시작하세요! 🎵✨**
