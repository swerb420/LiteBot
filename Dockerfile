FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . /app

WORKDIR /app/geminiBOT_LiteModev2

ENV PYTHONPATH=/app/geminiBOT_LiteModev2/src

ENTRYPOINT ["python3", "src/main.py"]
