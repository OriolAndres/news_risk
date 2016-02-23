
**Constructing an uncertainty index for Spain and assessing the predictive value on economic activity.**

We construct an economic uncertainty index (EU) and an economic policy uncertainty (EPU) index for Spain following the [policyuncertainty.com methodology](http://www.policyuncertainty.com/methodology.html) exploited in [Baker, Bloom and Davis][1] [BBD].

We base the index on the archives of [El Pais](http://elpais.com/), which is split between [1976 to 2012 editions](http://elpais.com/diario/) and [post 2012](http://elpais.com/archivo/).

Following [BBD][1], we conduct two different exercises to explore the impact of policy uncertainty on economic activity.  
First, we run a Vector Autoregression containing indicators for activity, inflation, government bond premium and Europe EPU index. We see that uncertainty has a negative and prolonged effect on activity. Uncertainty related to financial regulation and monetary policy have the largest impact.   
Second, we assemble a panel of stock quoted firm data including sectoral weight of public contracts, firm wage expenses, firm volatility and the EPU index, and run regressions that show that companies in sectors exposed to policy suffer increased correlation between stock volatility and the EPU index, and also they show less wage expenses growth when this uncertainty increases compared to less exposed companies.

---

# Project documentation

1. How to replicate
2. Presenting results

---

## 1. How to replicate

### Requirements

1. Python 2.7

2. Libraries
  * bs4
  * lxml
  * selenium
  * numpy
  * pandas
  * statsmodels
  * matplotlib
  * arch
  * inquisitor
  * python-levenshtein
  
3. chromedriver.exe

  [Download site](https://sites.google.com/a/chromium.org/chromedriver/downloads).

4. Inquirim API token

  [Create token](https://www.inquirim.com/account/api/). Used to retrieve macro data for the VAR computations.

### Project configuration

```
git clone https://github.com/OriolAndres/news_risk
```

Create settings.py file in top directory ("news_risk/settings.py") and define the following lines:

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

Write regular expressions for each company to match company strings extracted from BOE. Patterns have been stored already in accounts/biz_meta_regex.csv.

#### Get BOE
```python
from news_risk.boe import download_boe, catch_entities
download_boe() # download raw files containing awarded public works. Starts at 2005, ends at 2016.
catch_contractor_money() # extract who are awarded and how much they are paid
```

#### Get stocks from Invertia.com
```python
from news_risk.stocks import fetch_folder
fetch_folder() ## selenium (chrome) to fetch stock price data for all components of Mercado Continuo
calculate_cv() ## Uses GARCH(1,1) to get semi-annual conditional daily volatilities
```

#### Run regressions

European uncertainty index has previously been saved in [euro_news.csv](../blob/master/euro_news.csv). [Original xlsx file](http://www.policyuncertainty.com/media/Europe_Policy_Uncertainty_Data.xlsx) (policyuncertainty.com).

```python
from news_risk.elpais import get_quarterly_regressors
get_quarterly_regressors() ## get macro data from Inquirim, load European uncertainty index / build Spain indices (EPU & EU) 
from news_risk.accounts import run_regressions
run_regressions() ## Counts the projects each entity is awarded. Loads entity accounts data. Loads macro data. Runs firm level regressions
```

## 2. Presenting results

### Abstract

In this project we estimate a political uncertainty index for Spain.

In a first stage, we collect all the economy related articles from El Pais archives. We parse the body of articles and subset those that contain words related to both economy, policy, and uncertainty.

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


[1]: http://www.policyuncertainty.com/media/BakerBloomDavis.pdf