FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for the agent service
EXPOSE 8080

CMD ["python", "weather_agent.py"]
