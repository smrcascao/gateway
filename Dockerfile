#You must set environment variable: TEAMSWEBHOOK
FROM python:3.7
LABEL maintainer="smrcascao@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["pyhton", "-u", "app.py"]