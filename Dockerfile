FROM python:3.11
WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Execute the python file
CMD ["python", "/app/file.py"]
