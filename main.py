import argparse
from pathlib import Path

from eurlex_ds import EurLexDataset


def main(args: argparse.Namespace):

    dataset = EurLexDataset(data_root=args.data_root)
    print(f'Number of documents: {len(dataset)}')

    # Dump all concatenated docs in human readable text
    dataset.dump_to_txt(args.output_dir / 'all_txt.txt', mode='text')

    # Dump all document headers
    dataset.dump_to_txt(args.output_dir / 'stats.csv', mode='headers')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_root', type=Path)
    parser.add_argument('--output_dir', type=Path, default='./output')
    args = parser.parse_args()

    if not args.output_dir.is_dir():
        args.output_dir.mkdir(exist_ok=True, parents=True)

    main(args)
