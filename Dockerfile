FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

RUN mkdir -p /app/uploads

EXPOSE 5000

# app.py was renamed to main.py to avoid shadowing by app/ package; use main:app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
