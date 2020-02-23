FROM library/python:3.7-slim

COPY requirements.txt server.py /app/

WORKDIR /app

RUN pip3.7 install -r requirements.txt

EXPOSE 8001

CMD ["python", "./server.py"]
