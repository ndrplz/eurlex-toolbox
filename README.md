# eurlex

This repository contains a python toolbox to load, parse and process Official Journals of the European Union (EU).

## Overview

European Union law documents are publicly available in human-readable format in the [EUR-Lex portal](https://eur-lex.europa.eu/homepage.html). To enable automatic analysis, the same documents are released as structured text in the [EU Open Data Portal](https://data.europa.eu/euodp/en/home). Options for bulk download of entire blocks of documents are available there.

This software allows to handle the Official Journals of the EU as they are released in XML-Formex format [here](https://data.europa.eu/euodp/it/data/dataset/official-journals-of-the-european-union-in-english).

## Data preparation

The software assumes that the dataset of official journals has already been downloaded (from [here](https://data.europa.eu/euodp/it/data/dataset/official-journals-of-the-european-union-in-english)) and uncompressed in a directory `<eurlex_root>`. The expected directory hierarchy should be the following:
```bash
<eurlex_root>/
  ├── JOx_FMX_EN_2009/
    ├── file0.doc.xml
    ├── file0.xml
    ├── ...
    ├── fileN.doc.xml
    └── fileN.xml
  ├── JOx_FMX_EN_2010/
      ├── ...
  ├── ...
  └── JOx_FMX_EN_2019/
      ├── ...
```

## Hello World!
Once the dataset is in place, all documents can be dumped in human readable format with few lines of code.
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=<eurlex_root>)
print(f'Number of documents: {len(dataset)}')

# Dump all concatenated docs in human readable text
dataset.dump_to_txt('all_txt.txt', mode='text')

# Dump all document headers
dataset.dump_to_txt('stats.csv', mode='headers')
```
To save time, the `EurLexDataset` object can also be initialized form a text file containing a list of paths pointing to the docs to be loaded (see [here](https://github.com/anonymous-eurlex/eurlex-cfsp/blob/2bc7163c6aebe33fb5de73ddb4ea1df14226f8fa/eurlex_ds.py#L163-L174)).

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

* Filter the dataset keeping only CFSP documents (which was our initial focus):
```python
from eurlex_ds import EurLexDataset

dataset = EurLexDataset(data_root=args.data_root)
dataset.items[:] = [it for it in dataset if it.is_cfsp()]
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
