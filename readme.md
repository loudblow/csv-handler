# CSV Handler
CLI tool for filtering, sorting and aggregating CSV files.

# Installation
Insallation guide for MacOS/Linux
## 1. Clone the repository
```bash
git clone https://github.com/loudblow/csv-handler.git
```
## 2. Move to the project folder
```bash
cd csv-handler
```
## 3. Create venv
```bash
python3 -m venv .venv
```
## 4. Activate venv
```bash
source .venv/bin/activate
```
## 5.  Install dependencies
```bash
pip3 install -r requirements.txt
```
# Examples
## Output the contents of a file
```bash
$ python3 main.py --file products.csv
+------------------+---------+---------+----------+
| name             | brand   |   price |   rating |
+==================+=========+=========+==========+
| iphone 15 pro    | apple   |     999 |      4.9 |
+------------------+---------+---------+----------+
| galaxy s23 ultra | samsung |    1199 |      4.8 |
+------------------+---------+---------+----------+
| redmi note 12    | xiaomi  |     199 |      4.6 |
+------------------+---------+---------+----------+
| iphone 14        | apple   |     799 |      4.7 |
+------------------+---------+---------+----------+
| galaxy a54       | samsung |     349 |      4.2 |
+------------------+---------+---------+----------+
| poco x5 pro      | xiaomi  |     299 |      4.4 |
+------------------+---------+---------+----------+
| iphone se        | apple   |     429 |      4.1 |
+------------------+---------+---------+----------+
| galaxy z flip 5  | samsung |     999 |      4.6 |
+------------------+---------+---------+----------+
| redmi 10c        | xiaomi  |     149 |      4.1 |
+------------------+---------+---------+----------+
| iphone 13 mini   | apple   |     599 |      4.5 |
+------------------+---------+---------+----------+
```
## Filtering the contents
```bash
$ python3 main.py --file products.csv --where "brand=apple"
+----------------+---------+---------+----------+
| name           | brand   |   price |   rating |
+================+=========+=========+==========+
| iphone 15 pro  | apple   |     999 |      4.9 |
+----------------+---------+---------+----------+
| iphone 14      | apple   |     799 |      4.7 |
+----------------+---------+---------+----------+
| iphone se      | apple   |     429 |      4.1 |
+----------------+---------+---------+----------+
| iphone 13 mini | apple   |     599 |      4.5 |
+----------------+---------+---------+----------+
```
## Sorting the contents
```bash
$ python3 main.py --file products.csv --order-by="price=asc"
+------------------+---------+---------+----------+
| name             | brand   |   price |   rating |
+==================+=========+=========+==========+
| redmi 10c        | xiaomi  |     149 |      4.1 |
+------------------+---------+---------+----------+
| redmi note 12    | xiaomi  |     199 |      4.6 |
+------------------+---------+---------+----------+
| poco x5 pro      | xiaomi  |     299 |      4.4 |
+------------------+---------+---------+----------+
| galaxy a54       | samsung |     349 |      4.2 |
+------------------+---------+---------+----------+
| iphone se        | apple   |     429 |      4.1 |
+------------------+---------+---------+----------+
| iphone 13 mini   | apple   |     599 |      4.5 |
+------------------+---------+---------+----------+
| iphone 14        | apple   |     799 |      4.7 |
+------------------+---------+---------+----------+
| iphone 15 pro    | apple   |     999 |      4.9 |
+------------------+---------+---------+----------+
| galaxy z flip 5  | samsung |     999 |      4.6 |
+------------------+---------+---------+----------+
| galaxy s23 ultra | samsung |    1199 |      4.8 |
+------------------+---------+---------+----------+
```
## Aggregating the contents
```bash
$ python3 main.py --file products.csv --aggregate "price=med"
+-------+
|   med |
+=======+
|   514 |
+-------+
$ python3 main.py --file products.csv --aggregate "price=avg"
+-------+
|   avg |
+=======+
|   602 |
+-------+
```
# Testing
## Pytest
```bash
python3 -m pytest
```
## Coverage
93% test coverage
```bash
python3 -m pytest --cov
```