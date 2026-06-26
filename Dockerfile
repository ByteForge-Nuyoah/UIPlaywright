FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# Allure 报告生成依赖 Java；字体保证中文页面/报告正常显示。
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fonts-noto-cjk \
    openjdk-21-jre-headless \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

# 容器默认跑 headless，避免依赖显示器；需要报告时可覆盖 -report yes。
CMD ["python", "run.py", "-project", "clue", "-env", "test", "-mode", "headless", "-browser", "chromium", "-report", "no"]
