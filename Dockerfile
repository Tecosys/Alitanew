FROM python:3.9

RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python", "-m", "Alexa"]
