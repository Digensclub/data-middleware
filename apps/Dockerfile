# --- Stage 1: Build Stage ---
FROM python:3.13-slim AS builder

#Installing heavy stuff needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

#Copying requirements file and installing necessary packages from the file
COPY apps/requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

#--- Stage 2: Final Stage ---
FROM python:3.13-slim AS main-stage

# Copying the file into the image first so 'cat' can see it
COPY apps/packages.txt .

# We ONLY install curl here. 
# It's not redundant because this stage started from a fresh 'slim' image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    #pulling/ installing packages from data-middleware/apps/packages.txt path
    $(cat packages.txt) \
    && rm -rf /var/lib/apt/lists/* \
    && rm packages.txt

#Declaring Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONPATH="/home/appuser/.local/lib/python3.13/site-packages"

#Working Directory
WORKDIR /app

#1.Creating user first so directory exists
RUN useradd -m appuser

#2.Copying libraries from Stage 1 (builder) to appuser's home directory so appuser have permission to use them
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

#3. Switching to no-root user
USER appuser

#Exposing Network Port
EXPOSE 8000

#Gunicron + uvicorn combo to run docker container.
CMD ["gunicorn", "apps.main:app", \
     "--workers","9", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--bind", "0.0.0.0:8000"]

#--- uvicorn Only. Use below lines when running the app on Kubernets. Kubernets will handle the pod. ---
#IMP: Uncommit below lines and commit lines after Gunicron+uvicorn.
# CMD ["uvicorn", "apps.main:app" \
#      "--host", "0.0.0.0" \
#      "--port", "8000"]CMD ["uvicorn", "apps.main:app" \
#      "--host", "0.0.0.0" \
#      "--port", "8000"]