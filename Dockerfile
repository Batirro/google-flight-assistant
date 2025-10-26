# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies and Doppler CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && apt-get install -y doppler

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final image
FROM python:3.12-slim

WORKDIR /app

# Install Doppler CLI in final image
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && apt-get install -y doppler && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home appuser

RUN mkdir -p /app/data && chmod 755 /app/data
ENV DATA_DIR=/app/data

# Add user's local bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

USER appuser

# Copy installed packages from builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Expose port and define entrypoint
EXPOSE 8000
CMD ["doppler", "run", "--", "gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
