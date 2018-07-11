from bs4 import BeautifulSoup
import requests

DOWNLOAD_SIZE = 'large'

num_items = 50

base_url = 'https://www.vangoghmuseum.nl'

url = f'{base_url}/en/search/collection?q=&artist=Vincent%20van%20Gogh&pagesize={num_items}'

if __name__ == '__main__':

    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    teasers = soup.find_all('a', 'link-teaser')

    for teaser in teasers:
        # Get info about img from teaser
        title, period = teaser.h3.string.strip().split(',')
        period = period.strip()

        # Get the link to the content page for this image
        teaser_href = teaser.attrs['href']
        content_link = f'{base_url}{teaser_href}'

        # Get download link for image
        content_response = requests.get((content_link))

        content_soup = BeautifulSoup(content_response.content, "html.parser")

        [dl_button] = content_soup.find_all("a", "button", text=DOWNLOAD_SIZE)

        dl_href = dl_button.attrs['href']

        dl_link = f'{base_url}{dl_href}'

        print('\nDownloading:')
        print(f'Title: {title}')
        print(f'Period: {period}')
        image = requests.get(dl_link)

        fname = 'images/{}.jpg'.format(title)

        print('Writing to {}'.format(fname))

        with open(fname, 'wb') as f:
            f.write(image.content)

        print('done!\n')