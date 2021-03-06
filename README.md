[![Build Status](https://travis-ci.org/mini-kep/db.svg?branch=master)](https://travis-ci.org/mini-kep/db)
[![Assertible status](https://assertible.com/apis/56e34b07-ae3a-4248-937e-fef69d8ec2f2/status?api_token=VkiQoHOdjWU3vGv2)](https://assertible.com/dashboard#/services/56e34b07-ae3a-4248-937e-fef69d8ec2f2/results)
[![Coverage badge](https://codecov.io/gh/mini-kep/db/branch/master/graphs/badge.svg)](https://codecov.io/gh/mini-kep/db)

# Concept

`mini-kep` API allows to update and query a database of macroeconomic indicators.

# Quickstart

#### Query example

[This link](https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q&start_date=2016-01-01)
returns quarterly year-on-year Russian GDP growth rate as csv file, readable by R/pandas.

```
,GDP_yoy
2016-03-31,99.6
2016-06-30,99.5
2016-09-30,99.6
2016-12-31,100.3
2017-03-31,100.5
2017-06-30,102.5
```

#### Access code

`pandas` code for data access is [here](https://github.com/mini-kep/user-charts/blob/master/access.py).

#### Updating database

Administrator with API token can can also upload and delete data. This functionality 
is used by [parsers](https://github.com/mini-kep/parsers) to update dataset.


# API description 

Initial specification for database API is published [here](https://mini-kep.github.io/documentation/database/),
updates are documented below.

Endpoints:

  - `api/freq` - list avalable frequencies
  - `api/names/{freq}` - list variable names under specified frequency 
  - `api/info/?name={name}` - provide additional information about a variable
  - `api/datapoints` and `api/frame`- provide data 

#### GET ```freq```:

List avalable frequencies in the dataset. Returns ```{'a', 'q', 'm', 'd'}```.

- [api/freq](https://minikep-db.herokuapp.com/api/freq)


#### GET ```names```:

List variable names for specified frequency.

- [api/names/a](https://minikep-db.herokuapp.com/api/names/a)
- [api/names/q](https://minikep-db.herokuapp.com/api/names/q)
- [api/names/m](https://minikep-db.herokuapp.com/api/names/m)
- [api/names/d](https://minikep-db.herokuapp.com/api/names/d)

#### GET ```datapoints```:

Get subset of data as csv or json.

Args:
- `freq` - one of `a`, `q`, `m`, or `d` 
- `name` - variable name, ex: `GDP_yoy` 
- `start_date` (optional) - start date, ex: `2017-10-25`
- `end_date` (optional) - end date, ex: `2018-03-20`

Examples:

- [api/datapoints?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/datapoints?name=CPI_rog&freq=m)
- [api/datapoints?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/datapoints?name=GDP_yoy&freq=q)
- [api/datapoints?name=BRENT&freq=d&start_date=2017-01-01](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2017-01-01)
- [api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01](https://minikep-db.herokuapp.com/api/datapoints?name=USDRUR_CB&freq=d&start_date=2017-08-01&end_date=2017-10-01)

##### Parameter errors:
- [wrong freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=z&format=json)
- [wrong name for good freq](https://minikep-db.herokuapp.com/api/datapoints?name=ABC&freq=q&format=json)
- [start date in future](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2025-01-01)
- [end date > start date](https://minikep-db.herokuapp.com/api/datapoints?name=BRENT&freq=d&start_date=2015-01-01&end_date=2000-01-01)

#### GET ```frame```
Returns a csv dataframe.

Args:
- `freq` - one of `a`, `q`, `m`, or `d` 
- `names` - one variable name or several variable names separated by comma. Lists all variables, if omitted.
- `start_date` (optional) - start date, ex: `2017-10-25`
- `end_date` (optional) - end date, ex: `2018-03-20`


Example:

[api/frame?freq=d&names=BRENT,USDRUR_CB&start_date=2017-10-01&end_date=2017-10-10](http://minikep-db.herokuapp.com/api/frame?freq=d&names=BRENT,USDRUR_CB&start_date=2017-10-01&end_date=2017-10-10)

```,BRENT,USDRUR_CB
2017-10-02,55.67,
2017-10-03,56.12,57.8134
2017-10-04,56.0,57.9375
2017-10-05,57.09,57.7832
2017-10-06,55.5,57.5811
2017-10-07,,57.7612
2017-10-09,55.29,
2017-10-10,56.62,58.3151
```

Note: as standard csv composition, value will be skipped if there's no data for specified name and date (eg see line `2017-10-07,,57.7612` in example above).


Examples:
- [api/frame?freq=a](http://minikep-db.herokuapp.com/api/frame?freq=a)
- [api/frame?freq=m&names=CPI_rog,CPI_SERVICES_rog](http://minikep-db.herokuapp.com/api/frame?freq=m&names=CPI_rog,CPI_SERVICES_rog)
- [api/frame?freq=q&names=CPI_FOOD_rog,CPI_ALCOHOL_rog&start_date=2015-01-01](http://minikep-db.herokuapp.com/api/frame?freq=q&names=CPI_FOOD_rog,CPI_ALCOHOL_rog&start_date=2015-01-01)

#### GET ```info```:

Get a dictionary with variable description, allowed dates and latest values.

- [api/info?name=CPI_rog&freq=m](https://minikep-db.herokuapp.com/api/info?name=CPI_rog&freq=m)
- [api/info?name=GDP_yoy&freq=q](https://minikep-db.herokuapp.com/api/info?name=GDP_yoy&freq=q)
- [api/info?name=BRENT&freq=d](https://minikep-db.herokuapp.com/api/info?name=BRENT&freq=d)
- [api/info?name=USDRUR_CB&freq=d](https://minikep-db.herokuapp.com/api/info?name=USDRUR_CB&freq=d)

#### POST ```api/datapoints``` 

Upsert data from json, as described in [intial spec](https://mini-kep.github.io/documentation/database/#post).

Requires API token.

#### DELETE ```api/datapoints``` 

Upsert data dased on 

Requires API token.

#### New methods

More methods [discussed here](https://github.com/mini-kep/db/issues/8#issuecomment-336152762).


