# base image  
FROM python:3.11-slim

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

WORKDIR /app

# copy whole project to your docker home directory. 
COPY requirements.txt /app/
  
RUN pip install --upgrade pip  

# run this command to install all dependencies  
RUN pip install -r requirements.txt 

COPY . /app/
# port where the Django app runs  
EXPOSE 8000