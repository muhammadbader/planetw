import os

print("Hello Mubu!")
COPERNICUS_TOKEN = os.getenv("COPERNICUS_TOKEN")
COPERNICUS_SECRET = os.getenv("COPERNICUS_SECRET")
print(COPERNICUS_TOKEN)
print(COPERNICUS_SECRET)


import time
i = 0
while True:
    time.sleep(10)
    with open(f"/data/{i}.txt", "w+") as f:
        f.write(f"this is file {i}")
    i+=1
