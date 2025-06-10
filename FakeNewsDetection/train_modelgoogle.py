import requests

API_KEY = "AIzaSyDevMdD-M0ACW_k4nurtIqWiCFCCZaV_xg"
query = "COVID-19 vaccine"

url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code, response.text)
