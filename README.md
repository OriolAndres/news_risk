
**Constructing an uncertainty index for Spain and assessing the predictive value on economic activity.**

We construct an economic uncertainty index (EU) and an economic policy uncertainty (EPU) index for Spain following the [policyuncertainty.com methodology](http://www.policyuncertainty.com/methodology.html) exploited in [Baker, Bloom and Davis][1] [BBD].

We base the index on the archives of [El Pais](http://elpais.com/).

Following [BBD][1], we conduct two different exercises to explore the impact of policy uncertainty on economic activity.

First, we run a Vector Autoregression containing indicators for activity, inflation, sovereign spreads and European EPU index. We see that uncertainty has a negative and prolonged effect on activity. Uncertainty related to financial regulation and monetary policy have the largest impact. 

Second, in a panel of stock quoted firm data including sectoral weight of public contracts, firm wage expenses, firm volatility and the EPU index, we see that companies in sectors exposed to policy suffer increased correlation between stock volatility and the EPU index, and also they show less wage expenses growth when this uncertainty increases compared to less exposed companies.

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

Write regular expressions for each company to match the company strings extracted from BOE. Patterns have been stored already in [biz_meta_regex.csv](../master/accounts/biz_meta_regex.csv).

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

### Defining the indices.

We write a script to download the archive of El Pais, that runs from 4th May 1976 to today. The archive is split in two parts. The first system ([May 4th 1976 to February 7th 2012](http://elpais.com/diario/)) divides the daily editions into a handful of sections, including Economía, España and International. We focus on Economía. 71% of the editions contain between 10 and 30 articles in this section. In the second system ([February 7th 2012 to today](http://elpais.com/archivo/)) sections do not exist and instead they carry a number of tags, which we can easily use to filter the archive, and in particular we can filter the articles tagged with "Economía". In 70% of the days between 20 and 60 articles have the tag. We cannot assume that all the articles in the old Economía section would be tagged with "Economía" and that all the tagged articles with "Economía" would be filed in the Economía section. If the propensity to show uncertainty changed the index would be distorted.

We identify an article as showing economic uncertainty if it matches *both* of the following two conditions:

  * Contains *either* one of the regular expressions 'incertidumbre' and '\binciert'.
  * Contains the regular expression 'econ(o|ó)m(i|í)'

We identify an article as showing economic policy uncertainty if it matches both of the conditions above and it satisfies this condition:

  * Contains *either* of '\bimp(uesto|ositiv|onib)', '\btarifa', '\bregula(ci|ti|to)', '\bpol(i|í)tica', '\bgast(ar|o|a|os)\b', '\bpresupuest', '\bd(e|é)ficit', '\bbanc(o|a)[s]?[\s]*central', '\bbanco de españa', '\btribut'.
  
Then for both indices we sum all the matched articles in the month and divide by total number of articles in the month and escale the results to average 100.  
The third condition is rather broad and as a result the monthly correlation between both indices is 95.7%.

In the figure below we display the EPU index of Spain and of Europe.

![](figures/spain_v_europe.png?raw=true)

#### Additional decomposition

We create a number of categories to divide the uncertainty. These require the fulfilment of the EPU and the additional constraints that follow:

  * **Ingreso público**; '\bimp(uesto|ositiv|onib)','\btarifa','\brecauda','\btribut','\biva\b','\birpf\b'
  * **Gasto público**; '\bgast(ar|o|a|os)\b', '\bpresupuest', '(deuda|d(é|e)ficit) p(u|ú)blic', '\berario', 'pacto de estabilidad'
  * **Política monetaria**; '\bbanc(o|a)[s]?[\s]*central', '\bbce\b', '\bbde\b', '\bbanco de españa', 'pol(i|í)tica monetaria'
  * **Política sanidad**; '\bsani(tari|dad)', '\bhospital', '\bfarmac(ia|eu)', '\bm(e|é)dic(o|in)'
  * **Seguridad**; 'seguridad nacional', '\bmilitar', '\bterrorismo', '\beta\b', 'minist(erio|ro) de defensa', 'fuerzas armadas'
  * **Regulación bancaria**; 'supervis(ión|or) bancar', 'reformas? financiera', 'tests? de estrés', 'stress test', 'comisi(o|ó)n nacional', 'cnmv', 'fondo de (garant(i|í)a de )?dep(o|ó)sito', 'basilea'
  * **Regulación no bancaria**; '\bregula(ci|ti|to)', 'convenio', '\blegisla', '\bley(es)?\b', 'monopol', '\bc(a|á)rtel', '\bderecho'
  * **Sostenibilidad deuda**; 'deuda (sobera|p(ú|u)blic)', 'crisis de deuda', '\bdevalu', 'tipos? de cambio', '\bcambiari', '\beuro.?zona', '\brublo'
  * **Estado bienestar**; 'seguridad social', 'asuntos? social', 'estado del bienestar', 'subsidi(o|a)', 'fondos? estructural'
  * **Política comercial**; '\barancel', '\baduan(a|e)', 'tarifas?.{1,6}\b(expor|impor)', 'tratados?.{1,6}(libre.{1,6})?\bcomerc'
  * **Territorial**;  '\bdescentraliz', '\bindependent', '\bseparati', '\bsecesi(o|ó)n', '\bibarretx', '\bnacionalis', '\bterritorial'
  * **Política fiscal**; Match if **Ingreso público** and/or **Gasto público** are a match.
  * **Regulación**; Match if **Regulación bancaria** and/or **Regulación no bancaria** are a match.
  

### Vector Autoregressions

The objective of this section is evaluating the impact of uncertainty on activity. There are threats on the validity of our analysis if the uncertainty index is an endogenous variable like in these scenarios:

1 Lower GDP increases uncertainty. Lower gdp increases variance due to market discontinuities (sticky prices, debt and bankruptcy). In addition negative outcomes are psychologically difficult to assess.

2 Could it be that variance increasing policies are correlated with other policy features? Bad politicians are unpredictable.

We address the endogeneity challenges by including in the analysis variables that would largely overshadow the uncertainty index if the hypothesis were correct. If hypothesis 1 is correct then the uncertainty effect would be reduced by adding stock index volatility. We see that the effect of the uncertainty index remains stable across specifications.

#### Benchmark specification

We collect the European EPU from the [web](http://www.policyuncertainty.com) of the authors. Also data on long term government bonds rates for Spain and Germany assembled by Banco de España, we find the premium of spanish bonds and obtain the monthly change. Then we get from Base de datos de Series de Indicadores de Coyuntura Económica the producer price index for Spain and get monthly log changes. And finally we fetch the FEDEA index of the business cycle as a proxy for activity, and take the monthly change. The time series vector runs from September 1987 to December 2015.

We run a VAR with these 4 components and the EPU for Spain, adding 6 lags of data in the equation. Finally we make use of linear algebra to calculate the orthogonalized impulse response function, which describes the path of the system in response to an exogenous shock in a variable. That is accomplished by inverting the autoregressive system into a moving average representation. In the figure below we plot the results of a standard deviation shock in the EPU in the ensuing 12 months. Values refer to monthly changes.

![](figures/impulse_response.png?raw=true)

An increase in uncertainty of a standard deviation decreases the FEDEA index by 0.0441 after 12 months, a level which projected on real gdp would decrease growth by 0.0441\*0.043\*100 = 0.1914%. (4.3% is the cumulative effect of a full point shock in FEDEA on quarterly growth, estimated by VAR too.) The impact the shock of uncertainty in 2011 had in gdp growth was hence 0.63 %. ( (323 - 100) / 67 = 3.32; 3.32 \* 0.191 = 0.633 ).  
In the same setting we find that a 1 std negative shock in uncertainty increases the bond spread by 8.2 basis points and increases inflation by 0.06%, both 12 months after the shock.

#### Dissecting uncertainty

We run the same specification for the EPU, EU, and each of the uncertainty variants. In the next table we display the effects on GDP of an uncertainty shock, and also the number of articles containing the particular terms. We find that regulatory related uncertainty has the largest impact on GDP, while territorial and public revenue issues have a positive impact on activity.

Concept | Count | Effect on GDP (1 std negative shock)
--- | --- | ---
**Econ policy** | 5288 | -0.1915
**Econ general** | 6758 | -0.2120
**ingreso** | 1466 | 0.0554
**gasto** | 2624 | -0.1484
**money** | 2331 | -0.1737
**sanidad** | 396 | 0.0098
**seguridad** | 241 | -0.0230
**banca** | 292 | -0.3521
**othregula** | 1842 | -0.2853
**deuda** | 1491 | -0.0896
**bienestar** | 549 | -0.0068
**arancel** | 136 | -0.0049
**autonomia** | 337 | 0.1405
**fiscal** | 3129 | -0.1306
**regula** | 1986 | -0.3093

### Firm-level data

Given the complexity of any propositions based on VAR results, we set out to test again the implications of uncertainty on firm level data. We are going to ask whether sectors that are more exposed to public contracts reduce activity more in the face of policy uncertainty. Again, a company profit function may not be a linear function of sales, because of rigities in investment and labor, hence companies facing an increase in uncertainty scale back operations.

#### Assembling a panel

We are going to assemble a panel data for stock quoted companies in the Mercado Continuo of Bolsa de Madrid. We are going to assign them to a sector and find the relevance of public contracts in the sector. We will find stock volatility for each company, and also salary expenses and revenues. We will also include in some regressions government final consumption expenditure over gdp from BDSICE-MinEco.

##### Company reports

We get H1 and FY accounts from CNMV and for each company we get the salary expenses in the semester and sales. We use the sector classifications of CNMV.
The resulting panel has 345 companies, where many do not have a figure for wages and will be excluded. The earliest accounts included are from 2005 and the latest from 2015. Companies reporting usually does not span the full interval.

##### Text mining Boletin Oficial del Estado

We download BOE from 2005 to 2015 and find data on public work contracts. We use text mining to extract the value of the contract and the contractor name. Then we write regular expressions for the list of companies in the previous section and add up the volume of public work for each semester and company. Then we calculate the public work awards for each sector, and the fraction that represent over sales for the full time interval.

We manage to match the list of regular expressions against the BOE 9536 times for contracts worth 56.6 billion euro from 2005 to 2015. The largest contractor-year datum detected is Ferrovial in 2005. It received 37 contracts valued at 9 billion, which is probably biased upwards since some works may be split within coalitions of bidders.

We find that real estate development has the largest public work weight (6.9% of sales) followed by construction sector (4.7%), communication and transports 2.5% and chemicals 0.8%. On the other end, insurance and trade companies have negligible figures. Numbers are likely to be significantly biased downwards due to the difficulty of extracting company names from unstructured BOE documents, but this bias occurs in all sectors. It will be important to keep in mind that median sectoral public work accounts for 0.25% of total sales.

#### Conditional volatility

Finally, we get stock market returns for all quoted companies in the Mercado Continuo, and the IBEX 35. We do not have data on unlisted stocks. For each stock we calculate conditional volatility of each semester by estimating a GARCH(1,1) model on daily returns and averaging over the period.

### Panel regressions

#### EPU index effects on stock volatility

First we use volatility as a dependent variable. As regressors we will choose among the logarithm of the EPU index, the logarithm of the EPU index weighted by sectoral public work, the volatility of the IBEX 35 (again proxied by a GARCH(1,1)), the volatility of the IBEX 35 weighted by sectoral public work, public spending over GDP, and public spending over GDP weighted by sectoral public work.

If the EPU index increases, companies more exposed to public contracting should experience a larger increase in stock volatility, reflecting the concern that public contracting may decrease.

We report coefficient estimates and p-values right below.



Daily volatility | (1) | (2) | (3) | (4)
--- | :---: | :---: | :---: | :---:
**log_epu** | 9.916 |   | 10.747 |  
 | 0.373 |   | 0.365 |  
**epu_weighted** |   | 21.244 |   | 22.747
 |   | 0.132 |   | 0.131
**ibex35** |   |   | -1.791 |  
 |   |   | 0.839 |  
**ibex_weighted** |   |   |   | -3.326
 |   |   |   | 0.774
**spending** | -416.085 |   | -391.899 |  
 | 0.358 |   | 0.403 |  
**spend_weighted** |   | -672.074 |   | -627.692
 |   | 0.255 |   | 0.304
**lag_expend** |   |   |   |  
 |   |   |   |  
**r2** | 0.001 | 0.018 | 0.001 | 0.018
**N** | 1842 | 1842 | 1842 | 1842
**Time&firm eff.** | False | True | False | True


#### EPU index effects on salary expenses growth

In the second set of regressions, we will look at the evolution of variables in time. We use as dependent variable the firm semiannual log change in salary expenses. As regressors we modify slightly the previous variables. We use the first lag of log EPU (therefore assuming that salary expenses react with 6 months of delay), the first lag of log EPU weighted by sectorial public work, and the first lag of the change in public expenditure over gdp weighted by sector public work.


Log salary expense | (1) | (2) | (3) | (4)
--- | :---: | :---: | :---: | :---:
**log_epu** | -0.033 |   | -0.034 |  
 | 0.036 |   | 0.030 |  
**epu_weighted** |   | 0.226 |   | 0.842
 |   | 0.604 |   | 0.093
**ibex35** |   |   | 0.007 |  
 |   |   | 0.527 |  
**ibex_weighted** |   |   |   | -1.333
 |   |   |   | 0.011
**spending** | -0.956 |   | -1.091 |  
 | 0.179 |   | 0.142 |  
**spend_weighted** |   | 85.991 |   | 112.544
 |   | 0.113 |   | 0.041
**lag_expend** | -38.893 | -94.463 | -42.263 | -48.325
 | 0.363 | 0.090 | 0.327 | 0.399
**r2** | 0.016 | 0.081 | 0.017 | 0.084
**N** | 1642 | 1642 | 1642 | 1642
**Time&firm eff.** | False | True | False | True


![](figures/wage_growth_epu.png?raw=true)

![](figures/wage_growth_ratio.png?raw=true)

[1]: http://www.policyuncertainty.com/media/BakerBloomDavis.pdf