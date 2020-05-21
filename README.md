# eurlex

This repository contains a python toolbox to load, parse and process Official Journals of the European Union (EU).

## EU Law text corpus

:arrow_double_down: Download the dataset [here](https://drive.google.com/open?id=15zFcs7pmgmskS3Yn-FsijI-NuAHZNF5o).

Text corpus containing all the legal acts (the L series of the Official Journal) of the European Union adopted since the entry into force of the Lisbon Treaty, 1st December 2009, until 30th June 2019.

**The resulting corpus contains 24134 documents totalling approximately 43 million words.**

We present it divided in three files. 

* **Legislation** contains the legal acts the Union can adopt to exercise its competences (those listed under Article 288 Treaty on the Functioning of the European Union): regulations, directives, decisions, recommendations and opinions. It also contains the EU acts implementing them.
* **International Agreements and EEA acts** contains, in addition to Treaties concluded by the European Union, texts with EEA relevance.
* **Other** contains guidelines, interinstitutional agreements, notices, procedural rules, etc.

## Software Overview

European Union law documents are publicly available in human-readable format in the [EUR-Lex portal](https://eur-lex.europa.eu/homepage.html). To enable automatic analysis, the same documents are released as structured text in the [EU Open Data Portal](https://data.europa.eu/euodp/en/home). Options for bulk download of entire blocks of documents are available there.

This software allows to handle the Official Journals of the EU as they are released in XML-Formex format [here](https://data.europa.eu/euodp/en/data/dataset/official-journals-of-the-european-union-in-english).

## Data preparation
To maximize reproducibility and ease of use, the download and decompression of XML data from [here](https://data.europa.eu/euodp/en/data/dataset/official-journals-of-the-european-union-in-english) is automatized thanks to the `download_and_unzip.py` script. Usage:
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

## Citation

The code contained this repository accompanies the following publication:

> Palazzi, Andrea and Luigi Lonardo. "A Dataset, Software Toolbox, and Interdisciplinary Research Agenda for the Common Foreign and Security Policy", to appear in the European Foreign Affairs Review Vol. 25, Issue 2 (July 2020).

In case you find this dataset and toolbox helpful for your research (we hope so!), please mention the above paper.
