import re
import requests
from io import BytesIO
from tabula import read_pdf
from tabulate import tabulate
from bs4 import BeautifulSoup
from datetime import datetime


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
    response = requests.get(daily_url, verify=False)

    html = BeautifulSoup(response.text, "lxml")
    fileTable = html.find('article', class_="item-page").find('table')

    # find the latest link from the table by iterating backwards to check for valid links
    for row in reversed(fileTable.find("tbody").findAll('tr')):
        link_cell = row.findAll('td')[-1]
        link = link_cell.find('a')

        if link:
            file_url = link['href']
            response = requests.get(base_url + file_url, verify=False)
            return response.content
    return False


def get_rbz_rate(file_content: bytes):
    """
    Extracts the 'mid' exchange rate of the Zimbabwean dollar (ZWL) to the US dollar (USD) from a PDF file.
    :param file_content: the binary content of the pdf file
    :return: the zwl to usd mid rate or False if not found
    """

    # read in the pdf binary content as a pandas dataframe using tabula
    df = read_pdf(BytesIO(file_content), pages="all")

    # get data from every page
    for dt in df:
        html_body = tabulate(dt, headers='keys', tablefmt='html')
        html = BeautifulSoup(html_body, "lxml")
        table = html.find('table')
        zwlMidRateIndex = 8  # the index of the midrate in the table

        for row in table.findAll('tr'):
            if row.text.find("USD") != -1:
                # get the text from the inner-tags but separate them with a space
                row_text = row.get_text(" ", strip=True)
                rateList = row_text.split(" ")
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


