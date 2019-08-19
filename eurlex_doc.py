import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from xml.etree.cElementTree import iterparse

from parsing.legbase_parser import LegBaseParser
from parsing.location_parser import LocationParser
from parsing.tokenizer import Tokenizer


class EurLexFile:
    """
    Wrapper to EurLex file.
    """
    def __init__(self, file_path: Path):
        """
        Initialize an EurLex file.

        Args:
            file_path: File path.
        """
        if not isinstance(file_path, Path):
            raise ValueError('Please provide a valid Path.')
        if not file_path.is_file():
            raise OSError(f'File {file_path} does not exist.')

        self.file_path = file_path


class EurLexDataFile(EurLexFile):
    """
    Wrapper to EurLex data document.
    """
    def __init__(self, file_path: Path, tokenizer: Tokenizer, legbase_parser: LegBaseParser = None,
                 loc_parser: LocationParser = None):
        """
        Initialize EurLexDataFile.

        Args:
            file_path: File path.
            tokenizer: Tokenizer instance used for text tokenization.
        """
        try:
            super().__init__(file_path)
        except OSError:
            print(f'{file_path} does not exist.')
            return

        self.legal_bases = []
        if legbase_parser is not None:
            self.legal_bases.extend(legbase_parser.parse(self.file_path))

        root = ET.parse(self.file_path)

        # Load all text - notice how past elements are cleared
        self.text = '\n'.join(root.getroot().itertext())

        # One document can have multiple dates (e.g. L_2011313EN.01004501.xml)
        self.dates = [d.text for d in root.findall('BIB.INSTANCE/DATE')]

        # Format dates to yyyy/mm/dd (google sheet friendly)
        try:
            self.dates[:] = [datetime.strptime(d, '%Y%m%d').strftime('%Y/%m/%d') for d in self.dates]
        except ValueError:
            self.dates[:] = ['None']
            print(f'Unknown date format for: {self.file_path}.')

        # Possibly tokenize document text
        self.tokens = []
        if tokenizer is not None:
            self.tokens.extend(tokenizer(self.text))

        # Possibly find locations in text
        self.locations = {}
        if loc_parser is not None:
            self.locations = loc_parser(self.text)


class EurLexMetaFile(EurLexFile):
    """
    Wrapper to EurLex metadata document.
    """
    def __init__(self, file_path: Path):
        """
        Initialize EurLexMetaFile.

        Args:
            file_path: File path.
        """
        super().__init__(file_path)

        self.authors = []
        self.coll = None
        self.com = None
        self.legval = None
        self.title = ''

        self.main_pub = None
        self.sub_pubs = []

        # Read metadata of interest from the document
        path = []
        for event, elem in iterparse(file_path, events=('start', 'end')):
            if event == 'start':
                path.append(elem.tag)
                if elem.tag == 'TITLE' and 'PAPER' in path:
                    for t in elem.itertext():
                        self.title += t
            elif event == 'end':
                if elem.tag == 'AUTHOR' and elem.text is not None:
                    self.authors.append(elem.text)
                elif elem.tag == 'COM':
                    self.com = elem.text
                elif elem.tag == 'COLL':
                    self.coll = elem.text
                elif elem.tag == 'LEGAL.VALUE':
                    if path[-2] == 'DOC.MAIN.PUB':
                        # Be sure is the legal value of the main document
                        self.legval = elem.text
                elif elem.tag == 'REF.PHYS':
                    if path[-2] == 'DOC.MAIN.PUB':
                        self.main_pub = self.file_path.parent / elem.attrib['FILE']
                    elif path[-2] == 'DOC.SUB.PUB':
                        self.sub_pubs.append(self.file_path.parent / elem.attrib['FILE'])
                elem.clear()
                path.pop()

    def __str__(self):
        authors_str = '_'.join(self.authors)
        coll_str = self.coll
        legval_str = self.legval if self.legval is not None else "None"
        return ','.join([str(self.file_path), authors_str, coll_str, legval_str])

    def is_dec(self):
        """
        Determine whether current MetaFile belongs to a DEC document.
        """
        return self.legval in {'DEC', 'DEC.EEA', 'DEC_IMPL', 'DECIMP', 'DEC_DEL', 'DECDEL', 'DECIMPL'}
