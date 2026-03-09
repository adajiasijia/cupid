import requests
import json

response = requests.get('http://localhost:5000/api/news/financial')
result = response.json()
print(f"状态码：{response.status_code}")
print(f"返回数据：{json.dumps(result, ensure_ascii=False, indent=2)}")
