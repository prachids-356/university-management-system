# The container runs the console entry point by default. The Tkinter GUI needs a
# display, so it only works when an X11 socket is shared with the container
# (see README).
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-tk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY university/ ./university/
COPY tests/ ./tests/
COPY cli.py gui.py pyproject.toml ./

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UMS_DATA_FILE=/data/data.json

VOLUME ["/data"]

CMD ["python", "cli.py"]
