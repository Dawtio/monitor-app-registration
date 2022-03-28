FROM python:3.9-slim

LABEL maintainer="Maxime Brunet <mbrunet@dawtio.cloud>"

COPY . /app
WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["main.py"]
