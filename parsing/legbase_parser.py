from pathlib import Path
from xml.etree.cElementTree import iterparse


class LegBaseParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path):
        """
        Extract legal bases from EurLex XML data file.
        """
        return self.extract_legal_bases(file_path)

    @staticmethod
    def extract_legal_bases(file_path: Path):

        legal_bases = []

        for event, elem in iterparse(file_path, events=('start', 'end')):

            if event == 'start' and elem.tag == 'VISA':
                cur_base = ''
                for t in elem.itertext():
                    cur_base += t
                legal_bases.append(cur_base)

            elif event == 'end':
                elem.clear()

            # todo: we may break the loop before the whole doc is parsed

        return legal_bases
