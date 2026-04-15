import requests

TOKEN = "8066094820:AAFc5u6ApGi5aTQttJ9GXbUfPBmC9QicuXY"   # token của bạn
CHAT_ID = "1438278121"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

data = {
    "chat_id": CHAT_ID,
    "text": "Test message từ Python"
}

res = requests.post(url, data=data)

print("Status:", res.status_code)
print("Response:", res.text)