import os
import time

for i in range(2500):
    print(f"\n🚀 Running account {i+1}/15")
    os.system("python main.py")
    time.sleep(1)  # short pause between runs (optional)
