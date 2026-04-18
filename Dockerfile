FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev

ENV DELTA_MCP_TRANSPORT=http \
    DELTA_MCP_ENV=india_prod \
    DELTA_MCP_HTTP_HOST=0.0.0.0 \
    DELTA_MCP_HTTP_PORT=8000

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "delta-exchange-mcp"]
