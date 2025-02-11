FROM python:3.10-slim

WORKDIR /src

# Copy the dependency file and install packages using uv
COPY requirements.txt .

# Copy the startup script
COPY start_backend.sh .

COPY start_admin_panel.sh .

RUN ls -lah

# Copy the rest of the application source code
COPY ./src ./

RUN apt-get update && rm -rf /var/lib/apt/lists/*

# Install Ultra Violet (uv) package manager.
RUN pip install uv

RUN echo "Installing dependencies..." && \
    echo "uv version is $(uv --version)"

RUN uv venv .venv

# **Critical Step:** Add the virtual environment's bin directory to the PATH.
ENV PATH="/src/app/.venv/bin:$PATH"

RUN uv pip install --no-cache-dir -r requirements.txt

# Expose port 8000 and run the application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
