#use a lightwight python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

#Copy dependency file first
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy the application code
COPY . .

#Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
