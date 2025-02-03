import csv
import time
import logging
from datetime import datetime
from pathlib import Path
from faker import Faker
import random
from locust import HttpUser, task, between

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants for folder structure using Pathlib
PROJECT_ROOT = Path(__file__).parent.parent / "performance"
DATA_DIR = PROJECT_ROOT / "Data"
LOGS_DIR = PROJECT_ROOT / "Logs"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f'Create_user_post_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

# Request headers
HEADERS = {'Content-Type': 'application/json'}

fake = Faker()

def log_to_csv(data):
    """Write data to the log CSV file."""
    with open(LOG_FILE, "a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(data)

# Write CSV header
log_to_csv(["REQUEST_DATE", "REQUEST_TIME", "STATUS_CODE", "RESPONSE_SIZE_MB", 
            "RESPONSE_TIME", "SENT_PARAMETERS"])

class WebsiteUser(HttpUser):
    host = "http://localhost:8080/"
    wait_time = between(0.5, 1)

    @task
    def api_request(self):
        try:
            username = fake.user_name()
            API_URL = "http://localhost:8080/api/v3/user"
            payload = {
                "id": random.randint(10000, 99999), 
                "username": f"{username}",
                "firstName": f"{fake.first_name()}",
                "lastName": f"{fake.last_name()}",
                "email": f"{fake.email()}",
                "password": "testpass",
                "phone": f"{fake.phone_number()}",
                "userStatus": random.choice([0, 1])
            }
            start_time = time.time()
            response = self.client.post(url=API_URL, json=payload, headers=HEADERS, name="TC1S1")  
            end_time = time.time()

            log_data = [
                datetime.now().strftime('%Y-%m-%d'),
                datetime.now().strftime('%H:%M:%S'),
                response.status_code,
                str(round(len(response.content) / (1024 * 1024), 2)).replace('.', ','), 
                str(round(end_time - start_time, 1)).replace('.', ','),
                payload
            ]
            log_to_csv(log_data)

        except (ConnectionError, ValueError) as e:
            logging.error(f"Error during request: {e}")
            log_to_csv([datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S'), "-", "-", "-", "-", "-", str(e)])

# EXECUTION PARAMETERS:
# locust -f create_user_post.py --users 150 --web-port=8090 --spawn-rate 0 --run-time 60m
# locust -f create_user_post.py --users 50 --web-port=8090 --spawn-rate 0 --run-time 30m