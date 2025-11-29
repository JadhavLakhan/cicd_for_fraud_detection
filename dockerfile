# 1. Base Python Image
FROM python:3.11-slim

# 2. Work Directory
WORKDIR /apps

# 3. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy App Files
COPY . .

# 5. Expose Port
EXPOSE 8000

# 6. Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
