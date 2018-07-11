import os
import json
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

BASE_URL = 'https://www.vangoghmuseum.nl'
JOB_FPATH = 'job.json'


def get_job_details():
    """
    Load the job details and do some checks
    :return:
    """
    with open(JOB_FPATH, 'r') as f:
        job = json.load(f)

    if not os.path.isdir(job['output_dir']):
        raise FileNotFoundError(job['output_dir'] + 'does not exist')

    if not job['size'] in ['small', 'medium', 'large']:
        raise NotImplementedError(
            'size must be one of "small", "medium" or "large". You passed {}'.format(
                job['size']))

    if job['num_download'] < 0:
        raise NotImplementedError('Cannot pass num_download < 0')

    logging.info('Job details successfully loaded')
    return job


def get_dl_link(teaser):
    """
    get the image download link from a teaser tag

    :param teaser: bs4 tag
    :return:
    """
    logging.info('Parsing content for download link')
    # Get the link to the content page for this image
    teaser_href = teaser.attrs['href']
    content_link = f'{BASE_URL}{teaser_href}'

    # Get download link for image
    content_soup = BeautifulSoup(requests.get((content_link)).content,
                                 "html.parser")

    [dl_button] = content_soup.find_all("a", "button", text=job['size'])

    dl_href = dl_button.attrs['href']

    dl_link = f'{BASE_URL}{dl_href}'

    logging.info('Download link found')

    return dl_link


def download_img(img_url, title, output_dir):
    """

    :param img_url:
    :param title:
    :param output_dir:
    :return:
    """
    logging.info('Starting image download')
    image = requests.get(img_url)
    logging.info('Download done')

    fname = os.path.join(output_dir, f'{title}.jpg')

    if os.path.exists(fname):
        logging.warning(
            f'Tried to download {title} but file already existed under {output_dir}.')

    else:
        logging.info(f'Writing image to {fname}')
        with open(fname, 'wb') as f:
            f.write(image.content)

    logging.info(f'{fname} successfully saved.')

if __name__ == '__main__':

    logging.info('Started scraper')

    job = get_job_details()

    PAGE_URL = f'{BASE_URL}/en/search/collection?q=&artist=Vincent%20van%20Gogh&pagesize={job["num_download"]}'

    response = requests.get(PAGE_URL, timeout=20)

    soup = BeautifulSoup(response.content, "html.parser")

    teasers = soup.find_all('a', 'link-teaser')

    for teaser in teasers:
        # Get info about img from teaser
        title, period = teaser.h3.string.strip().split(',')
        period = period.strip()

        logging.info(f'Processing data for: {title}')

        dl_link = get_dl_link(teaser)

        download_img(dl_link, title, job['output_dir'])

        print('done!\n')
#
