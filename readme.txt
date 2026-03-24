================================================================================
OTL REPORTS - BUSINESS LOGIC
================================================================================

1. DATA SOURCE: INVOICE BOOKING DATA
--------------------------------------------------------------------------------
- Imported from Excel files or public Google Sheets links
- Two import methods:
  * Upload Excel file (.xlsx) directly
  * Paste a public Google Sheets URL (no credentials needed, sheet must be
    shared as "Anyone with the link")
- Excel/Google Sheet format: first 3 rows are system headers and must be skipped
- Row 4 contains the actual column headers (35 columns)
- Columns:
  Invoice No, Invoice Date, Revenue Date, month, Acc Code, Customer Name,
  Reference ID, Booking Code, Booking Master Desc, Booking Departure,
  Booking Category, Goods, Location From, Location To, Group Billing,
  Invoice Item Desc, Remarks, Currency, Quantity, Unit Price, Foreign Total,
  Foreign Tax, Foreign Total With Tax, Local Total, Local Tax,
  Local Total With Tax, Invoice Status, Last Modified User,
  Last Modified Date Time, Created By, Created Date Time, Actual Departure,
  Actual Arrival, Booking Requested Arrival, Fast Invoice, TWB

2. KEY KPIs
--------------------------------------------------------------------------------
- Total Invoices (distinct invoice numbers)
- Total Revenue (sum of Local Total)
- Total Tax (sum of Local Tax)
- Total Revenue with Tax (sum of Local Total With Tax)
- Total Customers (distinct customer names)
- Total Bookings (distinct booking codes)
- Average Revenue per Invoice
- Average Revenue per Customer

3. REPORTS & CHARTS
--------------------------------------------------------------------------------
- Revenue by Month: grouped by "month" field, shows revenue + tax bars
- Revenue by Category: grouped by Booking Category (doughnut chart)
- Top 10 Customers: ranked by total Local Total revenue
- Top Routes: Location From → Location To, ranked by revenue
- Invoice Status: count of invoices by status (pie chart)
- Revenue Summary: total revenue, tax, revenue incl. tax, averages

4. VISUALIZATIONS & FILTERS
--------------------------------------------------------------------------------
- Dashboard supports filtering by Month and Category (FTL/LTL)
- Month dropdown: filter all KPIs and charts for a specific month
- Category dropdown: filter by FTL or LTL to see separate reports
- FTL vs LTL Comparison chart: side-by-side bar chart of FTL and LTL
  revenue by month
- Top 10 Routes: horizontal bar chart showing top 10 routes
  (Location From → Location To) ranked by revenue, supports filters
- Dashboard has a currency selector dropdown (default: local currency)
  allowing users to view reports in different currencies
- All KPIs, charts, and summaries update dynamically when filters change
- Currency symbol is displayed BEFORE the value (e.g. VND 1,234,567.89)
- Booking Category values include: FTL - Domestic, FTL - Indochina,
  LTL - North Bound, LTL - South Bound (filtered using ILIKE %FTL% / %LTL%)

5. CURRENCY LOGIC
--------------------------------------------------------------------------------
- Invoice data has two sets of currency columns:
  * Foreign currency columns: Currency, Unit Price, Foreign Total, Foreign Tax,
    Foreign Total With Tax — these use the currency specified in each row
    (e.g. USD, THB, SGD). The "Currency" column indicates which foreign
    currency the row is denominated in.
  * Local currency columns: Local Total, Local Tax, Local Total With Tax —
    these are always in the local currency, regardless of the foreign currency.
- Local currency is configurable in Settings (default: VND)
- Dashboard currency selector behavior:
  * When local currency is selected (default): all KPIs and charts use
    Local Total, Local Tax, Local Total With Tax columns. All records are
    included regardless of their Currency column.
  * When a foreign currency is selected (e.g. USD, THB): all KPIs and charts
    use Foreign Total, Foreign Tax, Foreign Total With Tax columns. Only rows
    matching that specific Currency value are included in the results.
- Currency symbol is displayed BEFORE the value (e.g. VND 1,234,567.89)
- Tooltips on all charts display values with the selected currency label

6. INVOICE DATA PAGE
--------------------------------------------------------------------------------
- Table supports two view modes:
  * Standard: 12 key columns (Invoice No, Date, Customer, Booking Code,
    Category, From, To, Currency, Local Total, Tax, Total w/ Tax, Status)
  * Full View: all 35 columns including foreign currency columns, timestamps,
    goods, remarks, and departure/arrival dates
- Search behavior:
  * Search is triggered by pressing Enter or clicking the search icon
  * Searches across: Invoice No, Customer Name, Booking Code, Booking Master Desc
  * Case-insensitive partial match (ILIKE %term%)
  * Reset button clears the search and reloads all data
- Pagination:
  * 50 records per page
  * Shown above the table
  * Displays first 2 pages + current page ± 1 + last 2 pages with ellipsis
  * Shows record range and total count (e.g. "Showing 1–50 of 1,234 records")
- Export:
  * Export button downloads all current search results to .xlsx
  * File name: invoice_bookings_export.xlsx
  * Exports all matching records (not paginated — full result set)
  * Includes all columns; excludes internal "id" column

7. SETTINGS
--------------------------------------------------------------------------------
- Local Currency: configurable via Settings page (e.g. VND, USD, SGD)
  Affects display labels on dashboard KPIs, revenue summary, and chart tooltips

7. AUTHENTICATION
--------------------------------------------------------------------------------
- Session-based login
- SHA-256 password hashing with random salt
- Users must register and login before accessing reports
================================================================================
