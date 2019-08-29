"""
This script allows to download all the Official Journals of EU publicly
 available on data.europa.eu. The language of interest can be chosen by
 the user.

Usage:
    >>> python download_and_unzip.py <dataset_root> <language>
where:
    <dataset_root> is the directory that will contain the downloaded data
    <language> language of the downloaded journals
"""
import argparse
import re
import zipfile
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import requests
from tqdm import tqdm


class OJDownloader:
    """
    Helper class to make the downloading of OJ XML-F more readable.
    """
    def __init__(self):
        self.base_url = 'http://data.europa.eu/euodp/repository/ec/publ/op-jo-formex/'

    def download(self, out_dir: Path, lang: str, year: int):

        lang = lang.upper()

        lang_year_stem = f'JOx_FMX_{lang}_{year}'

        year_dir = out_dir / lang / lang_year_stem
        if not year_dir.is_dir():
            year_dir.mkdir(exist_ok=True, parents=True)

        # Download the "parent" zip, i.e. the bigger zip file that
        #  in turn contains many other smaller zip files
        parent_zip_path = out_dir / lang / f'{lang_year_stem}.ZIP'
        if not self._is_zip_valid(parent_zip_path):
            url = self.base_url + f'JOx_FMX_{lang}/{lang_year_stem}.ZIP'
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with parent_zip_path.open('wb') as f:
                    for chunk in tqdm(response,
                                      unit='bytes',
                                      unit_scale=128,
                                      total=self.get_content_len(url) // 128,
                                      desc=f'[{lang_year_stem}] Downloading...'):
                        f.write(chunk)

        # Extract the "parent" zip, i.e. this contains other archives
        # Notice: this zip file is not deleted even after extraction
        with ZipFile(parent_zip_path, "r") as zip_ref:
            zip_ref.extractall(year_dir)

        # Extract each of the sub-archives
        zip_files = list(year_dir.glob('*.zip'))
        for zip_path in tqdm(zip_files, desc=f'[{lang_year_stem}] Decompressing...'):
            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(year_dir)
            zip_path.unlink()

    def list_available_years(self, lang: str, verbose: bool = True):
        """
        Get the list of years for which the XML documents are available
         for the current language.
        """
        url = self.base_url + f'JOx_FMX_{lang.upper()}'

        page = requests.get(url).text

        # Match the `.ZIP` files in the page and get only the years
        pattern = re.compile(r'(?<=JOx_FMX_[A-Z]{2}_)\d{4}(?=.ZIP)')
        matches = pattern.findall(page)

        available_years = np.unique([int(m) for m in matches])
        if verbose:
            print(f'The following years are available for language ',
                  lang.upper(), ':', *available_years)

        return available_years

    @staticmethod
    def get_content_len(url: str):
        response = requests.head(url)

        if not response.ok:
            raise IOError(f'Impossible to reach: {url}')

        # Get file size to be able to show the progress during download
        try:
            content_len = int(response.headers['content-length'])
        except KeyError:
            content_len = -1

        return content_len

    @staticmethod
    def _is_zip_valid(f: Path):
        """
        Check whether the file is a valid zip file.
        """
        is_valid = f.is_file()

        if is_valid:
            try:
                ZipFile(f).testzip()
            except zipfile.BadZipFile:
                is_valid = False

        return is_valid


def main(args: argparse.Namespace):

    downloader = OJDownloader()

    years = downloader.list_available_years(lang=args.language)

    for year in years:
        downloader.download(args.dataset_root, lang=args.language, year=year)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_root', type=Path)
    parser.add_argument('language', type=str)

    args = parser.parse_args()

    # Sanity check on language argument
    valid_languages = {'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI',
                       'FR', 'GA', 'HR', 'HU', 'IT', 'LT', 'LV', 'MT', 'NL',
                       'PL', 'PT', 'RO', 'SK', 'SL', 'SV'}
    if args.language.upper() not in valid_languages:
        raise ValueError(f'Language "{args.language}" is not valid.',
                         f'Valid options: {", ".join(valid_languages)}')

    main(args)
