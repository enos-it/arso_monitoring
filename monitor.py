import base64
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CLIENT_ID = "API_TEL_3686949000"
CLIENT_SECRET = "Fg3IU0O2crkujkWuPgqpHlL3xAy6LfKP"
ACCESS_TOKEN_URL = "https://prijava-test.arso.gov.si/auth/realms/arso/protocol/openid-connect/token"
BASE_URL = "https://ismonitoring-test.arso.gov.si/api/integ"

KOMPLEKS_INSPIRE_ID = "SI.ARSO.000001283.FACILITY" # to je en podatek, index (kompleksInspireId)
MERILNO_MESTO = "KOTLOVNICA.1.PTK" # to je en podatek, index (merilnoMesto)

# Telemetrično sporočanje podatkov o dogodkih, posegih in spremembah v AMS in DAHS.
# /dogodekPosegSprememba
event = [
  {
    "kompleksInspireId": KOMPLEKS_INSPIRE_ID,
    "merilnoMestoOznaka": MERILNO_MESTO,
    "datumInCasZacetka": "2026-10-05T12:15:50",
    "datumInCasKonca": "2026-10-07T12:15:50",
    "uporabnik": "Enos",
    "modul": "Kotel1",
    "opomba": "Testni dogodek poseg sprememba",
    "siParameterSifra": "CO2",
    "siDogodekPosegSpremembaOznaka": "Testni dogodek poseg sprememba 1",
    "siStatusMeritevSimbol": "HIGH",
    "siObrStaNapTehEnoteSimbol": "NORM",
  }
]

# Telemetrično sporočanje vrednosti prvega nivoja (FLD).
# /vrednostiPrvegaNivoja
value = [
  {
    "kompleksInspireId": KOMPLEKS_INSPIRE_ID,
    "merilnoMestoOznaka": MERILNO_MESTO,
    "cas": "2022-03-10T12:15:50",
    "siObraStaNapTehEnoteSimbol": "string",
    "parameterSeznam": [
      {
        "siParameterSifra": "string",
        "siMerskaEnotaSifra": "string",
        "vrednostFld": 0.1,
        "siStatusMeritevSimbol": "strin"
      }
    ]
  }
]

# Telemetrično sporočanje kratkotrajnih povprečnih vrednosti STA, SSTA in VSTA.
# /kratkotrajnePovprecneVrednosti
value_avg = [
  {
    "kompleksInspireId": KOMPLEKS_INSPIRE_ID,
    "merilnoMestoOznaka": MERILNO_MESTO,
    "zapSt": 0,
    "casMeritve": "2022-03-10T12:15:50",
    "casInterval": 0,
    "siObrStaNapTehEnoteSimbol": "string",
    "casObratovanjaNaprave": 0,
    "parameterSeznam": [
      {
        "siParameterSifra": "string",
        "siMerskaEnotaSifra": "string",
        "vrednost": 0.1,
        "vrednostTip": "STA",
        "vrednotenjeSeznam": [
          {
            "mv": 0.1,
            "siMerskaEnotaSifra": "string",
            "siTipMejeSifra": "string",
            "siPreseganjeSimbol": "strin"
          }
        ],
        "pripadaSkupini": "obratovalnoStanjeNaprave"
      }
    ]
  }
]


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


def send_event(payload=event):
	token = get_access_token()
	request = Request(
		f"{BASE_URL}/dogodekPosegSprememba",
		data=json.dumps(payload).encode("utf-8"),
		headers={
			"Authorization": f"Bearer {token}",
			"Content-Type": "application/json",
		},
		method="POST",
	)

	with urlopen(request, timeout=30) as response:
		body = response.read()
		return json.loads(body) if body else None



if __name__ == "__main__":
	# print(send_event())
	print(get_measurement_sites())



