import requests
import time


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:147.0) Gecko/20100101 Firefox/147.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    curr_unix_timestamp_epoch = int(time.time())
    params = {
        # 'batch': '1-1769563341-0-1-0',
        'batch': f'1-{curr_unix_timestamp_epoch}-0-1-0',
        'lat': '37.789',
        'lon': '-122.394',
        'searchPath': 'san-francisco-ca/bia',
        'search_distance': '15',  # 15 miles
        'lang': 'en',
        'cc': 'us',
    }

    response = requests.get(
        'https://sapi.craigslist.org/web/v8/postings/search/full',
        params=params,
        # cookies=cookies,
        headers=headers,
    )

    if response.status_code == 200:
        print(response.json().get('data', {}).get("totalResultCount", 0))
    else:
        print(f"Error. {response.status_code=} ")


if __name__ == '__main__':
    main()
