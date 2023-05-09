import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


# a simple function that calls the get_latest_rate endpoint of the interbank api and therefor updates the database
def call_api():
    # http request settings
    # suppress warnings about insecure SSL certificate
    requests.packages.urllib3.disable_warnings()

    # setting verify to false to ignore SSL certificate verification (rbz doesn't have a valid certificate)
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    url = "https://kuda.pythonanywhere.com/interbank/get_latest_rate"
    response = http.get(url, verify=False, timeout=None)
    print(response.json())

8
def main():
    call_api()


if __name__ == '__main__':
    main()
