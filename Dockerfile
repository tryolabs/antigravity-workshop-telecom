FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GOOGLE_GENAI_USE_VERTEXAI=TRUE

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY data/ ./data/
COPY src/ ./src/
COPY mcp_server/ ./mcp_server/
COPY adk_agents/ ./adk_agents/
COPY scripts/ ./scripts/

RUN python data/seed_telecom_data.py

EXPOSE 8080

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
