FROM python:3.12.3

WORKDIR /app

COPY /mr_reviewer/requirements.txt .

RUN pip install -r requirements.txt

COPY mr_reviewer/ .

CMD ["sh", "-c", "python $SCRIPT"]

ENV SCRIPT=mr_reviewer/generate_response.py

