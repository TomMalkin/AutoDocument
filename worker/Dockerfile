FROM python:3.11

WORKDIR /worker

COPY /worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY autodoc /worker/autodoc 
