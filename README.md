# eurlex

This repository contains a python toolbox to load, parse and process Official Journals of the European Union (EU).

## Software Overview

European Union law documents are publicly available in human-readable format in the [EUR-Lex portal](https://eur-lex.europa.eu/homepage.html). To enable automatic analysis, the same documents are released as structured text in the [EU Open Data Portal](https://data.europa.eu/euodp/en/home). Options for bulk download of entire blocks of documents are available there.

This software allows to handle the Official Journals of the EU as they are released in XML-Formex format [here](https://data.europa.eu/euodp/it/data/dataset/official-journals-of-the-european-union-in-english).
## Data preparation
To maximize reproducibility and ease of use, the download and decompression of XML data from [here](https://data.europa.eu/euodp/it/data/dataset/official-journals-of-the-european-union-in-english) is automatized thanks to the `download_and_unzip.py` script. Usage:
```bash
python download_and_unzip.py <dataset_root> <language>
```
![download_en](./img/download_en.gif)

Once the `download_and_unzip` script has finished, the expected directory structure should look like the following:
```bash
<eurlex_root>/
  ├── JOx_FMX_EN_2004/
    ├── file0.doc.xml
    ├── file0.xml
    ├── ...
    ├── fileN.doc.xml
    └── fileN.xml
  ├── JOx_FMX_EN_2005/
      ├── ...
  ├── ...
  └── JOx_FMX_EN_2019/
      ├── ...
```

## Hello World!
Once the raw XML data are in place, the toolbox (entry point `main.py`) can be used to manipulate the data and create huamn readable text corpora. 

Documents can be dumped in human readable format in few lines of code.
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=<eurlex_root>)
print(f'Number of documents: {len(dataset)}')

# Dump all concatenated docs in human readable text
dataset.dump_to_txt('all_txt.txt', mode='text')

# Dump all document headers
dataset.dump_to_txt('stats.csv', mode='headers')
```
NB: To save time, the `EurLexDataset` object can also be initialized form a text file containing a list of paths pointing to the docs to be loaded (see [here](https://github.com/ndrplz/eurlex/blob/71cb848e3777fd42797d1863b4d0363f99272cfd/eurlex_ds.py#L164-L174)). This avoids listing all file on disk every time.

## Advanced features
The `EurLexDataset` object encapsulates the official journals dataset and it can be used to perform more sophisticated analyses and queries. Few examples:

* Create a separate text file for all the documents of each year from 2009 to 2019:
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=args.data_root)

for year in range(2009, 2020):
  items = [it for it in dataset if it.date.startswith(str(year))]
  year_all_txt = ('\n' * 5).join([it.to_txt() for it in items])
  Path(f'all_txt_{year}.txt').write_text(year_all_txt, encoding='utf-8')
```

* Filter the dataset keeping only decisions:
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=args.data_root)
dataset.items[:] = [it for it in dataset if it.meta.is_dec()]
```

* Print legal value and title of all documents to console:
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=args.data_root)
for item in dataset:
  print(f'{item.meta.legval}: {item.meta.title}\n')
```
etc.

Many other features are already available, but still undocumented since we are still working on them and the API might change a lot. These includes tokenization, extraction of geographical entities etc. However, the code is open source, so feel free to explore it and take what you may find useful :)
