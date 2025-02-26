FROM python:3.11
WORKDIR /app

RUN if [ ! -f /usr/local/bin/python ]; then ln -s /usr/local/bin/python3 /usr/local/bin/python; fi

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN which python3 && python3 --version
COPY . /app

# Execute the python file
CMD ["python3", "/app/file.py"]