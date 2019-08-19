from pathlib import Path
from typing import List
from typing import Union

from tqdm import tqdm

from eurlex_doc import EurLexDataFile
from eurlex_doc import EurLexMetaFile
from parsing.legbase_parser import LegBaseParser
from parsing.location_parser import LocationParser
from parsing.tokenizer import Tokenizer


class EurLexItem:
    """
    Single example of EurLexDataset.

    It is constituted by:
        - One metadata file
        - One main document
        - (Possibly) additional docs
    """
    def __init__(self, meta_doc: EurLexMetaFile, main_doc: EurLexDataFile, sub_docs: List[EurLexDataFile]):
        self.meta = meta_doc
        self.main_doc = main_doc
        self.sub_docs = sub_docs

    def __str__(self):
        """
        Each EurLexItem is represented by its metadata.
        """
        meta_str = str(self.meta)
        data_str = self.main_doc.dates[0]
        return ','.join([meta_str, data_str])

    def is_cfsp(self):
        """
        Determine whether this item is Common Foreign and Security Policy (CFSP)
        """
        valid_cfsp = False

        # The following docs have been manually marked as CFSP even though
        #  they don't satisfy the other requirements
        manually_selected = {
            'L_2009009EN.01005101.doc.xml', 'L_2010201EN.01003001.doc.xml', 'L_2014014EN.01000101.doc.xml',
            'L_2014205EN.01000201.doc.xml', 'L_2016074EN.01000101.doc.xml', 'L_2016300EN.01000101.doc.xml',
            'L_2017328EN.01003201.doc.xml'
        }
        if self.meta.file_path.name in manually_selected:
            valid_cfsp = True

        if 'cfsp' in self.meta.title.lower():
            valid_cfsp = True

        if self.meta.com == 'CFSP':
            valid_cfsp = True

        for author in self.meta.authors:
            if author in {'PSC', 'EEAS', 'PESC'}:
                valid_cfsp = True

        return valid_cfsp

    def to_txt(self):
        """
        Dump the current item as human readable text.
        """
        txt = ''
        txt += f'FILE_PATH: {self.meta.file_path}\n\n'
        txt += f'DATE: {self.date}\n\n'
        txt += f'TITLE: {self.meta.title}\n\n'
        txt += f'LEGVAL: {self.meta.legval}\n\n'
        txt += f'COLL: {self.meta.coll}\n\n'
        for author in self.meta.authors:
            txt += f'AUTHOR: {author}\n\n'
        txt += f'TEXT: {self.main_doc.text}\n\n'
        txt += f'TOKENS: {" ".join(self.main_doc.tokens)}\n\n'
        return txt

    @property
    def date(self):
        """
        Assume that the date of the item is the date of its main doc
        """
        return self.main_doc.dates[0]


class EurLexDataset:
    """
    Class modelling a dataset of EurLex documents.

    Attributes:
        data_root (str): Path to the dataset root.
        file_list (list of Path): List of files loaded.
        items (list of EurLexItem): List of dataset elements.
    """
    def __init__(self, data_root: Path, tokenize: bool = False,
                 parse_legal_bases: bool = False, parse_locations: bool = False):
        """
        Initialize the EurLexDataset loading all the documents.

        Args:
            data_root: Entry point for loading the documents.
                This can either be a directory or a text file containing
                the paths pointing to the docs to be loaded.
            tokenize: It True, data document text is split into tokens
                which are stored in each EurLexDataFile element.
            parse_legal_bases: If True, data documents are parsed looking
                for legal bases. Note: this may lead to a significant
                longer time for EurLexDataset init.
            parse_locations: If True, all data documents are parsed to
                find mentions of world locations. Note: this may lead to a
                significant longer time for EurLexDataset init.
        """
        self.data_root = data_root

        # Documents are created starting from `.doc.xml` files.
        self.file_list = self._list_meta_files(self.data_root)

        self.tokenizer = Tokenizer(filter_stopwords=True, check_is_alpha=True) if tokenize else None

        self.legbase_parser = LegBaseParser() if parse_legal_bases else None

        self.loc_parser = None
        if parse_locations:
            self.loc_parser = LocationParser(Path('./data/geo_info.csv'))

        self.items = []
        for f in tqdm(self.file_list):
            meta_doc = EurLexMetaFile(f)
            if meta_doc.is_dec():
                main_doc = EurLexDataFile(meta_doc.main_pub, self.tokenizer,
                                          self.legbase_parser, self.loc_parser)
                sub_docs = None  # todo: adding sub_docs causes a huge performance drop due to socket recv(?!)

                item = EurLexItem(meta_doc, main_doc, sub_docs)
                if item.is_cfsp():
                    self.items.append(item)

    def __getitem__(self, idx):
        return self.items[idx]

    def __len__(self):
        return len(self.items)

    def dump_to_txt(self, dump_file: Union[str, Path], enc: str = 'utf-8',
                    mode: str = 'headers'):
        """
        Dump to a unique text file all concatenated documents in
        a human readable format.
        """
        assert mode in {'headers', 'text'}

        if mode == 'headers':
            text = '\n'.join([str(it) for it in self.items])
        else:  # 'text'
            sep = '\n' * 2 + '%' * 50 + '\n' * 3
            text = sep.join([it.to_txt() for it in self.items])

        with Path(dump_file).open('wt', encoding=enc) as f:
            f.writelines(text)

    @staticmethod
    def _list_meta_files(data_root: Path):
        if not data_root.exists():
            raise OSError(f'{data_root} does not exist.')

        if data_root.is_file():
            with data_root.open('rt') as f:
                file_list = [Path(l.strip()) for l in f.readlines()]
        else:  # is a directory
            file_list = list(data_root.glob('**/*.doc.xml'))

        return file_list
