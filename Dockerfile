# 
FROM python:3.9-slim-buster

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
WORKDIR /code/app

# 
CMD ["uvicorn", "app.Tutorial:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
