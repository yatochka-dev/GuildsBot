FROM python:3.10-slim-buster

WORKDIR /app

COPY req.packages.txt req.packages.txt
RUN pip3 install -r req.packages.txt

COPY . .

CMD [ "python3", "bot.py" ]