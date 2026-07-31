# Power Query (Excel) Cleaning Steps

Reproduce the same cleaning pipeline as `scripts/clean_data.py` inside Excel's
Power Query Editor (Data → Get Data → From Text/CSV → Transform Data).

1. **Trim & clean text columns**
   `Transform → Format → Trim` and `Clean` on `customer_name`, `region`, `status`, `email`.

2. **Standardize casing**
   `Transform → Format → Capitalize Each Word` on `customer_name` and `region`.

3. **Replace blanks with "Unknown"**
   `Transform → Replace Values`: replace `null`/empty string with `"Unknown"` in
   `region` and `status`.

4. **Parse inconsistent dates**
   Add a Custom Column using M code that tries multiple formats:
   ```
   = try Date.FromText([signup_date], "en-US")
     otherwise try Date.FromText(Text.Replace([signup_date], "/", "-"), "en-US")
     otherwise null
   ```
   Then set the column data type to Date.

5. **Fix quantity/price**
   - Change `quantity` and `unit_price` to Decimal Number type (errors become `null`).
   - Replace negative or null `quantity` values with the column median:
     `Transform → Fill → Custom` or use
     `List.Median(Table.Column(#"PreviousStep","quantity"))` in a custom column.
   - Repeat for `unit_price`.

6. **Fill missing emails**
   Replace `null`/blank with `"unknown@missing.com"`.

7. **Remove duplicate rows**
   `Home → Remove Rows → Remove Duplicates` (based on all columns except the
   `record_id` index).

8. **Add calculated Revenue column**
   Add Custom Column: `= [quantity] * [unit_price]`.

9. **Load**
   `Close & Load To...` → load as a Table into a new worksheet named `Cleaned Data`.

This mirrors the exact transformations performed in `scripts/clean_data.py` and
`sql/clean_data.sql`, giving three equivalent implementations of the same
cleaning logic across Python, SQL, and Excel.
