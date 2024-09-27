FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /chalkmate_backend
WORKDIR /chalkmate_backend
ADD requirements.txt /chalkmate_backend/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /chalkmate_backend/