import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import BytesIO
import camelot
from tabulate import tabulate
from bs4 import BeautifulSoup
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


def download_rbz_pdf_binary():
    """
    Downloads the latest RBZ exchange rate PDF file and returns the binary content of the file.
    :return: binary content of the pdf file or False if not found
    """

    month = datetime.today().strftime("%B").lower()
    year = datetime.today().strftime("%Y")

    base_url = "https://www.rbz.co.zw/"
    daily_url = f"{base_url}index.php/research/markets/exchange-rates/13-daily-exchange-rates/1188-{month}-{year}"

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

    for i in range(5):
        try:
            response = http.get(daily_url, verify=False, timeout=None)
            html = BeautifulSoup(response.text, "lxml")
            fileTable = html.find('article', class_="item-page").find('table')

            # find the latest link from the table by iterating backwards to check for valid links
            for row in reversed(fileTable.find("tbody").findAll('tr')):
                link_cell = row.findAll('td')[-1]
                link = link_cell.find('a')

                if link:
                    file_url = link['href']
                    response = http.get(base_url + file_url, verify=False, timeout=None)
                    logger.info(
                        'Download file: {} (status {})'.format('success ' if response.status_code == 200 else 'failed',
                                                               response.status_code))
                    # return response.content

                    with open("rbz.pdf",
                              "wb") as f:  # save the pdf file to the filesystem and return the path to the file
                        f.write(response.content)
                    return os.path.abspath("rbz.pdf")

        except requests.exceptions.RequestException as e:
            logger.info("Attempt {} failed with error: {}".format(i + 1, e))
            continue

    return False


def get_rbz_rate(filename: str):
    """
    Extracts the 'mid' exchange rate of the Zimbabwean dollar (ZWL) to the US dollar (USD) from a PDF file.
    :param filename: the binary content of the pdf file
    :return: the zwl to usd mid rate or False if not found
    """

    # read in the pdf binary content as a pandas dataframe using camelot
    tables = camelot.read_pdf(filepath=filename, pages="all")

    # delete the pdf file
    os.remove(filename)

    # get data from every page
    for table in tables:
        df = table.df
        zwlMidRateIndex = 8  # the index of the midrate in the table

        for index, row in df.iterrows():
            if "USD" in row.to_string():
                rateList = row.to_string().split(" ")
                rateList = [item for item in rateList if item != '']
                rate = rateList[zwlMidRateIndex]

                # remove commas and spaces from the rate
                rate = re.sub(",", "", rate)
                rate = re.sub("(\d) (\d)", r"\1\2", rate)

                return float(rate)
    return False


def main():
    try:
        print("Getting latest RBZ pdf file...")
        latest_pdf_binary = download_rbz_pdf_binary()
        if latest_pdf_binary:
            print("Getting RBZ ZWL-USD rate...")
            midrate = get_rbz_rate(latest_pdf_binary)
            if midrate:
                print(f"RBZ ZWL-USD rate: {midrate}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()


