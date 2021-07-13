import requests


def test_get_site(site_url: str):
    print(f"Testing: {site_url}, result=", end="")
    x = requests.get(site_url)
    if x.status_code == 200:
        print('Success')
    else:
        print('Failure')


def main():
    test_get_site('https://www.google.com')


if __name__ == "__main__":
    main()
