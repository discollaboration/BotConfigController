FROM python:3.9
COPY requirements.txt ./
RUN pip install -r requirements.txt
WORKDIR bot/
COPY . ./
CMD ["python", "main.py"]