FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD gunicorn -k aiohttp.worker.GunicornWebWorker -b 0.0.0.0:$PORT wsgi
