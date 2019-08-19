import re
from collections import defaultdict
from pathlib import Path


def read_geo_table(table_file: Path, encoding: str = 'utf-8',
                   sep: str = '\t', comment: str = '#'):
    """
    Read the csv file with geographical entities and returns the dictionary
    of words that must be searched.

    Args:
        table_file: File containing the words that will be matched.

            Each row of the file is structured as follows:
            Key,Country,Capital,Nationality,other_0,...,other_n

            Each row contains a list words. The first entry of the row
            is the key used to aggregate results. Second to fourth columns
            indicates the country name, the capital and nationality.
            Other column possibly indicate additional cities or region in
            the same area (the area is given by the key).
        encoding: File encoding.
        sep: Column separator (used to split each row).
        comment: Lines starting with `comment` are ignored.

    Returns geo_dict: Dictionary of geographical entities.
    """
    if not table_file.is_file():
        raise OSError(f'File {table_file} does not exist.')
    lines = table_file.read_text(encoding=encoding).split('\n')
    lines = [l for l in lines if not l.startswith(comment)]
    lines = filter(None, lines)  # remove empty rows

    lines = [list(filter(None, l.split(sep))) for l in lines]
    geo_dict = {line[0]: line[1:] for line in lines}
    return geo_dict


class GeoRegex:
    """
    The GeoRegex object encapsulates the regular expression needed to find a
     geographic place, together with possible pre-processing
    """
    def __init__(self, geo_name: str, whole_word: bool = True,
                 ignore_case: bool = True):
        self.plain_name = geo_name

        self.pattern = self._preprocess(self.plain_name)

        if whole_word:
            self.pattern = rf'\b{self.pattern}\b'

        self.flags = re.IGNORECASE if ignore_case else 0
        self.regex: re.Pattern = re.compile(self.pattern, self.flags)

    def finditer(self, text: str):
        return self.regex.finditer(text)

    @staticmethod
    def _preprocess(name: str):
        # todo: this could be performed a-priori automatically over all keys
        conversion_dict = {
            'Balkans': '(?<!Western )Balkans',
            'Sudan': '(?<!South )Sudan',
            'Mediterranean': '(?<!Southern )Mediterranean',
            'Vatican': 'Vatican(?! City)',
            'Czech': 'Czech(?! Republic)',
            'Swiss': 'Swiss(?! Confederation)',
            'Palestinian': 'Palestinian(?! Territor)'
        }
        return conversion_dict.get(name, name)


class LocationParser:

    def __init__(self, geo_info_file: Path):
        """
        Object that looks for occurrences of geographical places in text.

        Args:
            geo_info_file: File containing the words that will be matched.

                Each row of the file is structured as follows:
                    Key,Country,Capital,Nationality,other_0,...,other_n

                Each row contains a list words. The first entry of the row
                is the key used to aggregate results. Second to fourth columns
                indicates the country name, the capital and nationality.
                Other column possibly indicate additional cities or region in
                the same area (the area is given by the key).
        """
        geo_dict = read_geo_table(geo_info_file, sep=',')

        # In these phase, we try to match all words, whether they are
        #  countries, capitals, nationalities, regions etc.
        all_geo_names = [name for country in geo_dict.values() for name in country]

        # Remove duplicates, since some capitals are called as their country
        #  and they would appear twice (e.g. Luxembourg)
        all_geo_names = list(set(all_geo_names))

        # Compile regexes for faster and more readable reuse
        self.regexes = [GeoRegex(name) for name in all_geo_names]

    def __call__(self, text: str):
        """
        Parse `text` and return the a dict of location occurrences.
        """
        # todo: keep track of the index of each match
        locations = defaultdict(int)
        for regex in self.regexes:
            matches = list(regex.finditer(text))
            if matches:
                locations[regex.plain_name] += len(matches)
        return locations
