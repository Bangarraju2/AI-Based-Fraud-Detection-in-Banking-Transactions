"""
FraudShield AI — Continuous Transaction Simulator
Generates and posts synthetic transactions to the API to simulate real-world banking traffic.
"""

import requests
import random
import time
import argparse
import signal
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"
SIMULATOR_EMAIL = "simulator@example.com"
SIMULATOR_PASS = "sim_pass_2024"

class TransactionSimulator:
    def __init__(self, delay=5, api_url=API_BASE_URL):
        self.delay = delay
        self.api_url = api_url
        self.token = None
        self.running = True
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, *args):
        print("\nStopping simulator...")
        self.running = False

    def authenticate(self):
        """Register or Login to get the JWT token."""
        print(f"Authenticating as {SIMULATOR_EMAIL}...")
        
        # Try login
        try:
            resp = requests.post(f"{self.api_url}/auth/login", json={
                "email": SIMULATOR_EMAIL,
                "password": SIMULATOR_PASS
            })
            
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                print("Login successful.")
                return True
                
            # If login failed, try register
            if resp.status_code == 401:
                print("User not found. Registering simulator user...")
                resp = requests.post(f"{self.api_url}/auth/register", json={
                    "email": SIMULATOR_EMAIL,
                    "password": SIMULATOR_PASS,
                    "full_name": "Traffic Simulator Bot",
                    "role": "analyst"
                })
                
                if resp.status_code == 201:
                    self.token = resp.json()["access_token"]
                    print("Registration successful.")
                    return True
            
            print(f"Authentication failed: {resp.text}")
            return False
            
        except requests.ConnectionError:
            print(f"[ERROR] Could not connect to API at {self.api_url}. Is the backend running?")
            return False

    def generate_features(self, is_fraud=False):
        """Generate random V1-V28 features, with optional fraud shift."""
        features = {}
        
        # Standard noise for all transactions
        base_std = 1.5 if not is_fraud else 3.0
        
        for i in range(1, 29):
            val = random.gauss(0, base_std)
            
            # Apply known fraud shifts from the ML training pipeline
            if is_fraud:
                if i == 1: val -= 3.0
                elif i == 2: val += 2.5
                elif i == 4: val += 2.0
                elif i == 10: val -= 2.5
                elif i == 12: val += 3.0
                elif i == 14: val -= 2.0
                elif i == 17: val -= 2.5
                
            features[f"v{i}"] = round(val, 6)
            
        return features

    def simulate_one(self):
        """Send a single transaction."""
        is_fraud = random.random() < 0.1 # 10% chance of high-risk attempt
        features = self.generate_features(is_fraud)
        
        # Generate Realistic Amount
        if is_fraud:
            amount = random.expovariate(1/1500) # Average $1500 for fraud
        else:
            amount = random.expovariate(1/150) # Average $150 for legit
            
        payload = {
            "amount": round(amount, 2),
            "time": time.time() % 172800, # Mock time relative to a 2-day period
            **features
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            start_time = time.time()
            resp = requests.post(f"{self.api_url}/transactions/", json=payload, headers=headers)
            elapsed = time.time() - start_time
            
            if resp.status_code == 201:
                result = resp.json()
                ts = datetime.now().strftime("%H:%M:%S")
                color = "\033[91m" if result['risk_category'] == 'HIGH' else ("\033[93m" if result['risk_category'] == 'MEDIUM' else "\033[92m")
                reset = "\033[0m"
                
                print(f"[{ts}] {color}{result['risk_category']:>6}{reset} | ${amount:>9.2f} | Score: {result['fraud_score']:.4f} | API: {elapsed*1000:>3.0f}ms")
            elif resp.status_code == 401:
                print("Token expired. Re-authenticating...")
                if self.authenticate():
                    self.simulate_one()
            else:
                print(f"[ERROR] API returned {resp.status_code}: {resp.text}")
                
        except requests.ConnectionError:
            print("[ERROR] Lost connection to API.")
            time.sleep(5)

    def run(self, count=None):
        if not self.authenticate():
            return

        print("-" * 65)
        print(f"{'TIMESTAMP':<10} | {'RISK':<6} | {'AMOUNT':>9} | {'SCORE':<7} | {'LATENCY':<7}")
        print("-" * 65)
        
        i = 0
        while self.running:
            self.simulate_one()
            i += 1
            if count and i >= count:
                break
            time.sleep(self.delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FraudShield AI Transaction Simulator")
    parser.add_argument("--delay", type=float, default=5, help="Delay between transactions in seconds")
    parser.add_argument("--count", type=int, default=None, help="Number of transactions to send (None for infinite)")
    parser.add_argument("--url", type=str, default=API_BASE_URL, help="API Base URL")
    
    args = parser.parse_args()
    
    sim = TransactionSimulator(delay=args.delay, api_url=args.url)
    sim.run(count=args.count)
