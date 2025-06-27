FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
RUN pip install pyopenssl

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 5000

# 애플리케이션 실행
CMD ["python", "app.py"] 