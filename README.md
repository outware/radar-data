# Radar data fetch

## Description
Extracts and transforms data within a Google Spreadheet into JSON suitable for using in the Tech Radar.

## Installation
```sh
pip install -r REQUIREMENTS.txt
```

## Configuration
Generate a Google Service Account Client ID JSON credential file, see [Using OAuth 2.0 for Server to Server Applications](https://developers.google.com/identity/protocols/OAuth2ServiceAccount).

Rename the downloaded JSON key to credentials.json and place along side the radar.py script.

## Running
```sh
python radar.py --spreadsheet "My Radar Data" --worksheet "iOS" > radar.json
```

## License
Refer to [LICENSE](LICENSE).
