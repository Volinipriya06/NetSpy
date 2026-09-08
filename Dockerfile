FROM python:3.9-slim

LABEL org.opencontainers.image.title="NetSpy" \
      org.opencontainers.image.description="Local Network & Port Discovery Utility"

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY netspy.py /app/netspy.py

ENTRYPOINT ["python", "/app/netspy.py"]
CMD []
