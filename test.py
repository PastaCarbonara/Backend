import requests


url = "https://munchie.azurewebsites.net/api/latest"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNUJkV2xPM2x6cXh5RXA4ZyIsImV4cCI6MTY4ODExNjU0Nn0.zWcGpEkKdl3tC5-awueMSIO9nYXNy-a8vGAk-WLaslU"}

response = requests.get(f"{url}/groups", headers=headers)

print(response.status_code)
groups_json = response.json()

for group in groups_json:
    print(group.get("id"))

    resp = requests.delete(f"{url}/groups/{group.get('id')}", headers=headers)

    if resp.status_code != 204:
        print("ERROR ON", group.get("id"))
        print(resp.status_code)
        print(resp.json())
        break

    print("gone.")


print(len(groups_json))
