# Data Cleaning & Transformation (Excel, SQL & Python)

Cleans, structures, and transforms a messy raw customer/order export into an
analysis-ready dataset, ensuring accuracy and consistency. The same cleaning
logic is implemented three ways — Python/Pandas, SQL, and documented Power
Query steps for Excel — so the project shows versatility across tools.

## Data Quality Issues Fixed
| Issue | Example | Fix |
|---|---|---|
| Inconsistent name casing/spacing | `"MARY JONES"`, `"  Bob Lee"` | Trim + title case + collapse whitespace |
| Inconsistent region casing, missing values | `"north"`, `"EAST"`, blank | Standardize casing, fill blanks with `Unknown` |
| Inconsistent date formats | `2023-05-01`, `05/01/2023`, `01-05-2023` | Parse against multiple known formats into a single ISO date |
| Inconsistent/missing status | `"active"`, `"INACTIVE"`, blank | Standardize casing, fill blanks with `Unknown` |
| Missing/invalid quantity | blank, `-1` | Treat as missing, impute with median |
| Missing unit price | blank | Impute with median price |
| Missing email | blank | Flag as `unknown@missing.com` |
| Exact duplicate rows | 3 injected duplicate records | Removed via de-duplication logic |

## Repo Structure
```
2-data-cleaning-transformation/
├── data/
│   ├── raw_customer_orders.csv       # Messy source data (260+ rows)
│   └── cleaned_customer_orders.csv   # Output after cleaning
├── scripts/
│   └── clean_data.py                 # Pandas cleaning pipeline
├── sql/
│   └── clean_data.sql                # Equivalent cleaning logic in SQL
├── power_query_steps.md              # Step-by-step Excel/Power Query equivalent
└── README.md
```

## How to Run (Python)
```bash
cd scripts
pip install pandas
python clean_data.py
```
This reads `data/raw_customer_orders.csv` and writes `data/cleaned_customer_orders.csv`.

## How to Run (SQL)
Load `data/raw_customer_orders.csv` into a `raw_customer_orders` table, then run
`sql/clean_data.sql` against your database (PostgreSQL syntax; minor tweaks needed
for MySQL/SQL Server).

## How to Run (Excel / Power Query)
See `power_query_steps.md` for the equivalent M-code / UI steps to reproduce this
cleaning pipeline inside Excel's Power Query editor.

## Result
Cleaning removed all duplicate rows, standardized categorical fields (region,
status), unified date formats, and imputed missing numeric values — producing
a dataset ready for downstream reporting and reducing data-quality errors that
would otherwise break aggregation and pivoting.

## Tools Used
`Python` · `Pandas` · `SQL` · `Excel` · `Power Query`
