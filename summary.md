## Abstract

In this project we estimate a political uncertainty index for Spain.

---

Concept | Count | Cumulative effect
--- | --- | ---
matches | 5288 | -0.0469
eumatches | 6758 | -0.0564
ingreso | 1466 | 0.0082
gasto | 2624 | -0.0377
money | 2331 | -0.0425
sanidad | 396 | -0.0015
seguridad | 241 | -0.0029
banca | 292 | -0.0898
othregula | 1842 | -0.0714
deuda | 1491 | -0.0231
bienestar | 549 | -0.0221
arancel | 136 | -0.0052
autonomia | 337 | 0.0260
fiscal | 3129 | -0.0358
regula | 1986 | -0.0771


![](figures/spain_v_europe.png?raw=true)


### How to replicate


#### Requirements

1. Python 2.7

2. Libraries
..* bs4
..* lxml
..* selenium
..* pandas
..* statsmodels

3. chromedriver.exe
... Downloadable [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).
4. Inquirim API token. 
... [Here](https://www.inquirim.com/account/api/) to create one. Used to retrieve macro data for the VAR computations.

#### Project configuration

```
git clone https://github.com/OriolAndres/news_risk
```

create settings.py file in top directory ("news_risk/settings.py") and define the following lines:

```python
import os
token = '<inquirim_api_token>' ## https://www.inquirim.com/account/api/ 
chromedriver = r"<path_to_chromedriver>\chromedriver.exe" 
download_dir = r'<default_download_directory_chrome/firefox>'
rootdir = os.path.abspath(os.path.dirname(__file__))
```

#### Download El Pais files and find keywords: 
```python
from news_risk.elpais import start_from_scratch
start_from_scratch() # downloads full economy archive from El Pais (1976-2016), matches articles against conditions
```

#### Get company Q2 / annual reports from CNMV
```python
from news_risk.accounts import fetch_folder, fetch_list_by_sector, unzip, parse_xml
fetch_folder() # selenium (firefox) iterates over all companies to get all their reports
unzip() # zip to plain text
parse_xml() # extract company name, sales and salary expenses
fetch_list_by_sector() # list companies in each sector
```

#### Intermediate step

Write regular expressions for each company to use to match companies extracted from BOE. Patterns in accounts/biz_meta_regex.csv.

#### Get BOE
```python
from news_risk.boe import download_boe, catch_entities
download_boe() # get awarded public works per year
catch_contractor_money() # extract who are awarded and how much they are paid
```

#### Get stocks from Invertia.com
```python
from news_risk.stocks import fetch_folder
fetch_folder() ## selenium (chrome) to fetch stock price data for all components of Mercado Continuo
```

### Run 