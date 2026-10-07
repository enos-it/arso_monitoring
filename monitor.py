import base64
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CLIENT_ID = "API_TEL_3686949000"
CLIENT_SECRET = "Fg3IU0O2crkujkWuPgqpHlL3xAy6LfKP"
ACCESS_TOKEN_URL = "https://prijava-test.arso.gov.si/auth/realms/arso/protocol/openid-connect/token"
BASE_URL = "https://ismonitoring-test.arso.gov.si/api/integ"


def get_access_token():
	credentials = base64.b64encode(
		f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
	).decode("ascii")
	request = Request(
		ACCESS_TOKEN_URL,
		data=urlencode({"grant_type": "client_credentials"}).encode("ascii"),
		headers={
			"Authorization": f"Basic {credentials}",
			"Content-Type": "application/x-www-form-urlencoded",
		},
		method="POST",
	)

	with urlopen(request, timeout=30) as response:
		token_response = json.load(response)

	return token_response["access_token"]


def get_measurement_sites(change_timestamp="2026-10-07T12:00:00.000"):
	token = get_access_token()
	url = (
		f"{BASE_URL}/prenosArsoSifrant/readEvMerilnoMestoSeznam?"
		f"{urlencode({'changeTimestamp': change_timestamp})}"
	)
	request = Request(
		url,
		headers={"Authorization": f"Bearer {token}"},
		method="POST",
	)

	with urlopen(request, timeout=30) as response:
		return json.load(response)



if __name__ == "__main__":
	print(get_measurement_sites())



