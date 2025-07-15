FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . /app

WORKDIR /app/geminiBOT_LiteModev2

ENTRYPOINT ["python3", "-m", "src.main"]
