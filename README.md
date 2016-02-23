
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
  
3. chromedriver.  

  [Download site](https://sites.google.com/a/chromium.org/chromedriver/downloads).  
  Note: Selenium-Firefox issues a prompt each time a .asp file is downloaded for confirmation. Changing 'browser.helperApps.neverAsk.saveToDisk' profile option didn't make effect.

4. Inquirim API token

  [Create token](https://www.inquirim.com/account/api/). Used to retrieve macro data for the VAR estimation.

### Project configuration

```
$ git clone https://github.com/OriolAndres/news_risk
```

Create settings.py file in top directory ("news_risk/settings.py") and define the following lines:

```python
import os
token = '<inquirim_api_token>' ## https://www.inquirim.com/account/api/ 
chromedriver = r"<path_to_chromedriver>\chromedriver.exe" 
download_dir = r'<download_directory_chrome_and_firefox>'
rootdir = os.path.abspath(os.path.dirname(__file__))
```

#### Download El Pais files and find keywords: 

Caveat: Downloading the full archive generates 60 GB of files and may take several days depending on your internet connection and the behavior of the servers of elpais. It is recommended to split the job in parallel instances.

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

Write regular expressions for each company to match the company strings extracted from BOE. Patterns have been stored already in accounts/biz_meta_regex.csv.

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

#### Estimate VAR

```python
from news_risk.elpais import estimate_VAR
estimate_VAR()
```

#### Run firm level regressions

European uncertainty index has previously been saved in [euro_news.csv](../master/euro_news.csv). [Original xlsx file](http://www.policyuncertainty.com/media/Europe_Policy_Uncertainty_Data.xlsx) (policyuncertainty.com).

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


### Definig the indices.

We create a script to download the archive of El Pais, that runs from 4th May 1976 to today. The archive is split in two parts. The first system ([May 4th 1976 to February 7th 2012](http://elpais.com/diario/)) divides the daily editions into a handful of sections, including Economía, España and International. We focus on Economía. 71% of the editions contain between 10 and 30 articles in this section. In the second system ([February 7th 2012 to today](http://elpais.com/archivo/)) sections do not exist and instead they carry a number of tags, which we can easily use to filter the archive, and in particular we can filter the articles tagged with "Economía". In 70% of the days between 20 and 60 articles have the tag. We cannot assume that all the articles in the old Economía section would be tagged with "Economía" and that all the tagged articles with "Economía" would be filed in the Economía section. This adds noise to the index if the propensity of articles to show uncertainty changes across the systems.

We identify an article as showing economic uncertainty if it matches *both* of the following two conditions:

  * Contains *either* one of the regular expressions 'incertidumbre' and '\binciert'.
  * Contains the regular expression 'econ(o|ó)m(i|í)'

We identify an article as showing economic policy uncertainty if it matches both of the conditions above and it satisfies this condition:

  * Contains *either* of '\bimp(uesto|ositiv|onib)', '\btarifa', '\bregula(ci|ti|to)', '\bpol(i|í)tica', '\bgast(ar|o|a|os)\b', '\bpresupuest', '\bd(e|é)ficit', '\bbanc(o|a)[s]?[\s]*central', '\bbanco de españa', '\btribut'.
  
Then for both indices we sum all the matched articles in the month and divide by total number of articles in the month and escale the results to average 100.  
The third condition is rather broad and as a result the monthly correlation between both indices is 95.7%.

#### Additional decomposition

We create a number of categories to divide the uncertainty. These require the fulfilment of the EPU and the additional constraints that follow:

  * **Ingreso** '\bimp(uesto|ositiv|onib)','\btarifa','\brecauda','\btribut','\biva\b','\birpf\b'
  
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