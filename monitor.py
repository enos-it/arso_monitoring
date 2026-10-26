import base64
import json
from enum import Enum
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class DogodekPosegSpremembaOznaka(Enum):
    REDNI_PREGLED = "TM-ESVZ-01"
    IZREDNI_PREGLED = "TM-ESVZ-02"
    VZDRZEVANJE = "TM-ESVZ-03"
    ZAMENJAVA = "TM-ESVZ-04"
    QAL_2 = "TM-ESVZ-05"
    AST = "TM-ESVZ-06"
    SPREMEMBA_KALIBRACIJSKE_FUNKCIJE = "TM-ESVZ-07"
    SPREMEMBA_PARAMETROV_ZA_VREDNOTENJE = "TM-ESVZ-08"
    SPREMEMBA_V_PROGRAMSKI_KODI = "TM-ESVZ-09"
    IZKLOP_DAHS_NAPRAVA_NE_OBRATUJE = "TM-ESVZ-10"
    IZKLOP_DAHS_NAPRAVA_OBRATUJE = "TM-ESVZ-11"
    VKLOP_DAHS = "TM-ESVZ-12"
    DRUGO = "TM-ESVZ-13"


CLIENT_ID = "API_TEL_5852498000"
CLIENT_SECRET = "EX5FL7WE0LHSiFgNiSdA7nXrouCpGmcf"
ACCESS_TOKEN_URL = "https://prijava-test.arso.gov.si/auth/realms/arso/protocol/openid-connect/token"
BASE_URL = "https://ismonitoring-test.arso.gov.si/api/integ/v2"

KOMPLEKS_INSPIRE_ID = "SI.ARSO.000113159.FACILITY" # to je en podatek, index (kompleksInspireId)
MERILNO_MESTO = "MMZ16" # to je en podatek, index (merilnoMesto)

# Telemetrično sporočanje podatkov o dogodkih, posegih in spremembah v AMS in DAHS.
# /dogodekPosegSprememba
event = [
  {
    "kompleksInspireId": KOMPLEKS_INSPIRE_ID,
    "merilnoMestoOznaka": MERILNO_MESTO,
    "datumInCasZacetka": "2026-10-08T12:15:50",
    "datumInCasKonca": "2026-10-08T13:15:50",
    "uporabnik": "Enos",
    "modul": "Kotel1",
    "opomba": "Testni dogodek poseg sprememba",
    "siParameterSifra": "PAR_000657",
    "siDogodekPosegSpremembaOznaka": DogodekPosegSpremembaOznaka.REDNI_PREGLED.value,
    "siStatusMeritevSimbol": "V",
    "siObrStaNapTehEnoteSimbol": "SO",
  }
]

# Telemetrično sporočanje vrednosti prvega nivoja (FLD).
# /vrednostiPrvegaNivoja
value = [
  {
    "kompleksInspireId": KOMPLEKS_INSPIRE_ID,
    "merilnoMestoOznaka": MERILNO_MESTO,
    "cas": "2026-10-13T12:13:50",
    "siObraStaNapTehEnoteSimbol": "NP",
    "parameterSeznam": []
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
    "siObrStaNapTehEnoteSimbol": "NORM",
    "casObratovanjaNaprave": 0,
    "parameterSeznam": [
      {
        "siParameterSifra": "PAR_000657",
        "siMerskaEnotaSifra": "string",
        "vrednost": 0.1,
        "vrednostTip": "STA",
        "vrednotenjeSeznam": [
          {
            "mv": 0.1,
            "siMerskaEnotaSifra": "string",
            "siTipMejeSifra": "string",
            "siPreseganjeSimbol": "string"
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


def get_measurement_sites(api="readEvMerilnoMestoSeznam",change_timestamp="2026-10-07T12:00:00.000"):
	token = get_access_token()
	url = (
		f"{BASE_URL}/prenosArsoSifrant/{api}?"
		f"{urlencode({'changeTimestamp': change_timestamp})}"
	)
	request = Request(
		url,
		headers={"Authorization": f"Bearer {token}"},
		method="POST",
	)

	with urlopen(request, timeout=30) as response:
		return json.load(response)


def send_event(api="dogodekPosegSprememba", payload=event):
	print(f"Sending event: {json.dumps(payload, indent=2)}")
	token = get_access_token()
	request = Request(
		f"{BASE_URL}/api",
		data=json.dumps(payload).encode("utf-8"),
		headers={
			"Authorization": f"Bearer {token}",
			"Content-Type": "application/json",
		},
		method="POST",
	)

	try:
		with urlopen(request, timeout=30) as response:
			body = response.read()
			return json.loads(body) if body else None
	except HTTPError as error:
		response_body = error.read().decode("utf-8", errors="replace")
		raise RuntimeError(
			f"ARSO event request failed with HTTP {error.code}: {response_body}"
		) from error



if __name__ == "__main__":
	print(send_event(api="dogodekPosegSprememba", payload=event))
	# print(get_measurement_sites(api="readEvMerilnoMestoSeznam", change_timestamp="2026-10-07T12:00:00.000"))

