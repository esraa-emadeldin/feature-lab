# Production image for the tumour second-opinion API.
# Build:  docker build -t tumour-api .
# Run:    docker run -p 8000:8000 tumour-api
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY serve.py .

# Train while building, so the image always contains a model made with
# the exact library versions it will run with.
RUN python -m src.train

EXPOSE 8000
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]
