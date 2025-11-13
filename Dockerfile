FROM python:3.9
RUN apt-get update && apt-get install -y git python3-pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /TwitchBot
WORKDIR /TwitchBot
ENTRYPOINT ["python", "-u", "twitch.py"]
