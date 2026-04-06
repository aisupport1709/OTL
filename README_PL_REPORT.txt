================================================================================
                    OTL P&L REPORT APPLICATION
           Báo cáo Kết quả Hoạt động Kinh doanh (P&L Report)
================================================================================

PROJECT OVERVIEW
================================================================================
The OTL P&L Report application is a specialized financial reporting tool that
processes Vietnamese accounting data (from "911 t" and "154 t" files) and
generates comprehensive Profit & Loss (P&L) statements on a monthly and annual
basis.

The system automatically identifies and aggregates financial data by leaf-node
account codes (excluding parent/summary accounts) and calculates all key P&L
metrics following standard accounting principles.


SYSTEM REQUIREMENTS
================================================================================

1. FILE INPUT FORMATS
   - Excel files (.xlsx, .xls)
   - Google Sheets (publicly accessible links)

2. SUPPORTED FILE TYPES
   - "911 t" (P&L Aggregation) - Contains revenue and expense accounts
   - "154 t" (Cost of Production) - Contains COGS accounts
   - "SDCK 1541" (Ending Balance) - Ending inventory balance data

3. FILENAME REQUIREMENTS
   - Must contain date pattern: DD.MM.YYYY or DD-MM-YYYY
   - Examples:
     * "911 t 01.02.2026-28.02.2026.xlsx"
     * "154 t 01-02-2026-28-02-2026.xlsx"
     * "SDCK 1541 28.02.2026.xlsx"

   Filename parsing:
     - Date range or single date must be present to extract month and year
     - Example: "01.02.2026" → Month 2, Year 2026 (always uses first date)


FILE STRUCTURE & COLUMN MAPPING
================================================================================

INPUT EXCEL COLUMN REQUIREMENTS:

   Column 1: Tk đ.ứng (Account Code)
   - Format: Numeric code (e.g., 5111, 51131, 511311)
   - System strips Excel's .0 float suffix during import
   - Non-numeric codes preserved as-is (e.g., "5113A")

   Column 2: Tên tk đ.ứng (Account Name)
   - Text description of the account
   - Example: "SALARY - CARGO & CONTAINER"

   Column 3: Ps nợ (Debit Amount)
   - Numeric value
   - Used for expense/cost accounts

   Column 4: Ps có (Credit Amount)
   - Numeric value
   - Used for revenue/income accounts

COLUMN DETECTION:
   - System auto-detects columns by header name (case-insensitive)
   - If headers not found by name, falls back to positional detection
   - First two columns = Account Code + Account Name


SUB-ACCOUNT FILTERING RULES (CRITICAL)
================================================================================

LEAF-NODE DETECTION:

   The system identifies only "leaf" account codes - accounts with NO children
   in the dataset. This prevents double-counting of aggregated amounts.

   EXAMPLE HIERARCHY:
   Given accounts: {511, 5113, 51131, 511311, 511312, 51132}

   Parent accounts (EXCLUDED):
   - 511       (parent of 5113, 51131, 511311, 511312, 51132)
   - 5113      (parent of 51131, 511311, 511312)
   - 51131     (parent of 511311, 511312)
   - 51132     (standalone)

   Leaf accounts (INCLUDED):
   - 511311    ✓ (no children)
   - 511312    ✓ (no children)
   - 51132     ✓ (no children)

DETECTION ALGORITHM:
   - Per (month, file_type, account_prefix) group, identify codes with no
     other codes starting with them
   - A code is a leaf if: no other code in the set starts with this code

DEBIT/CREDIT SELECTION RULES:
   - Revenue accounts (511x, 515x, 711x): Use Ps CÓ (Credit) values
   - Expense/Cost accounts (6xx, 8xx, 642x, 635x, 811x): Use Ps NỢ (Debit) values
   - File type "154 t" with accounts starting with 6 or 8: Always use Ps NỢ


P&L CALCULATION LOGIC
================================================================================

STEP 1: IDENTIFY ACCOUNT GROUPS (By Prefix)

   Revenue Accounts (File: 911 t):
   - 511x  → Doanh thu thuần (Net Revenue)         [Use: Ps Có (Credit)]
   - 515x  → Doanh thu HĐTC (Financial Revenue)    [Use: Ps Có]
   - 711x  → Thu nhập khác (Other Income)          [Use: Ps Có]

   Expense Accounts:
   - 154x / 6xx, 8xx (File: 154 t) → Giá vốn hàng bán (COGS) [Use: Ps Nợ (Debit)]
   - 642x (File: 911 t) → Chi phí QLDN (Operating Expenses)  [Use: Ps Nợ]
   - 635x (File: 911 t) → Chi phí tài chính (Finance Costs)  [Use: Ps Nợ]
   - 811x (File: 911 t) → Chi phí khác (Other Expenses)      [Use: Ps Nợ]


STEP 2: AGGREGATE LEAF-NODE AMOUNTS

   For each (month, file_type, account_prefix) group:
   1. Identify all accounts
   2. Calculate leaf nodes (accounts with no children)
   3. Sum ONLY leaf-node values, NOT parent account totals


STEP 3: CALCULATE P&L LINE ITEMS (Sequential)

   Line 1: Doanh thu thuần (Net Revenue)
   = Sum of Ps Có from all leaf codes starting with 511x

   Line 2: Giá vốn hàng bán (Cost of Goods Sold - COGS)
   = Sum of Ps Nợ from all leaf codes (6xx, 8xx) in "154 t" file

   Line 3: Lợi nhuận gộp (Gross Profit)
   = Doanh thu thuần - Giá vốn hàng bán

   Line 4: Chi phí QLDN (Operating Expenses)
   = Sum of Ps Nợ from all leaf codes starting with 642x (911 t file)

   Line 5: Lợi nhuận thuần từ HĐKD (Operating Profit)
   = Lợi nhuận gộp - Chi phí QLDN

   Line 6: Doanh thu HĐTC (Financial Revenue)
   = Sum of Ps Có from all leaf codes starting with 515x (911 t)

   Line 7: Chi phí tài chính (Finance Costs)
   = Sum of Ps Nợ from all leaf codes starting with 635x (911 t)

   Line 8: Thu nhập khác (Other Income)
   = Sum of Ps Có from all leaf codes starting with 711x (911 t)

   Line 9: Chi phí khác (Other Expenses)
   = Sum of Ps Nợ from all leaf codes starting with 811x (911 t)

   Line 10: Lợi nhuận trước thuế (Profit Before Tax)
   = Operating Profit + (Financial Revenue - Finance Costs)
                      + (Other Income - Other Expenses)
   = Lợi nhuận HĐKD + (DTTC - CPTC) + (TN khác - CP khác)


P&L REPORT OUTPUT FORMAT
================================================================================

DISPLAY STRUCTURE:
   - Rows: 10 P&L line items + sub-account details
   - Columns: 12 months (Tháng 1-12) + Annual Total (Tổng Năm)

LINE ITEM ORDER:
   1. Doanh thu thuần (Net Revenue)
   2. Giá vốn hàng bán (COGS)
   3. Lợi nhuận gộp (Gross Profit) [SUBTOTAL - highlighted green]
   4. Chi phí QLDN (Operating Expenses)
   5. Lợi nhuận thuần từ HĐKD (Operating Profit) [SUBTOTAL - highlighted green]
   6. Doanh thu HĐTC (Financial Revenue)
   7. Chi phí tài chính (Finance Costs)
   8. Thu nhập khác (Other Income)
   9. Chi phí khác (Other Expenses)
   10. Lợi nhuận trước thuế (Profit Before Tax) [SUBTOTAL - highlighted green]

SUBTOTAL ROWS (Auto-Highlighted):
   - Lợi nhuận gộp (Line 3)
   - Lợi nhuận thuần từ HĐKD (Line 5)
   - Lợi nhuận trước thuế (Line 10)

SUB-ACCOUNT DISPLAY:
   - Each main line item shows contributing sub-account codes below it
   - Sub-accounts are indented and use smaller font
   - Format in browser: indented name with account code
   - Format in Excel: separate "Chỉ Tiêu" (name) and "Mã TK" (code) columns

NUMBER FORMATTING:
   - Thousand separator: 1,000,000 (comma-separated)
   - Negative numbers: Displayed in parentheses without minus sign
   - Example: (1,000,000) instead of -1,000,000
   - Zero values: Displayed as "-" (dash)


WEB APPLICATION FEATURES
================================================================================

PAGE: /pl/ (P&L Report Dashboard)
   - Year selector dropdown (auto-loads available years from database)
   - Main P&L table with:
     * Sticky left column (Chỉ Tiêu + Mã TK) when scrolling horizontally
     * Main line items with bold formatting and colored backgrounds
     * Sub-account rows (indented, smaller font, light background)
     * Monthly data (Tháng 1-12)
     * Annual totals (Tổng Năm)
   - Export Excel button (downloads formatted xlsx file)
   - "No data" state with link to import page when year has no data

PAGE: /pl/import (Import & Map P&L Data)

   SECTION 1: Import Local PL Data
   - Import Local PL Data modal
     * Excel Files tab: Drag & drop or select .xlsx/.xls files
     * Google Sheets tab: Paste public Google Sheets URL(s)
     * Supports batch import of multiple files
     * Shows import results with success/error count
   - Clear All button: Delete all P&L data (with confirmation)

   SECTION 2: Map Local Account Code to HQ Account (Account Mapping)
   - Import Mapping: Upload mapping rules from Excel/Google Sheets
   - Edit Mapping: Popup modal to add/edit/delete account mappings
   - Export: Download current mappings as Excel file
   - Clear All: Remove all mappings (with confirmation)

   Mapping Features:
     * Store local account code → HQ account code relationships
     * Reusable for future reconciliation/consolidation
     * Upsert on re-import (update if exists, insert if new)
     * Account codes stored without .0 suffix


ACCOUNT MAPPING FEATURE
================================================================================

PURPOSE: Map local Vietnamese account codes to HQ standardized codes

MAPPING FILE FORMAT:
   Column 1: Account code (e.g., 62211)
   Column 2: HQ account name/code (e.g., "SALARY - CARGO & CONTAINER")

STORAGE:
   - AccountMapping table in database
   - local_code (unique): Original code
   - hq_code: Target code/description

IMPORT BEHAVIOR:
   - Upsert: If account already exists, update HQ code
   - No "skip if exists" - allows re-importing with updates
   - Strips .0 float suffix from numeric codes
   - Handles both Excel and Google Sheets

USAGE:
   - Currently stored for future use (not actively used in P&L calculation)
   - Can be integrated into future consolidation/reporting features


DATA IMPORT WORKFLOW
================================================================================

STEP 1: UPLOAD FILES
   - Go to /pl/import → "Import Data" button
   - Upload "911 t" and "154 t" Excel files
   - Or paste Google Sheets URLs
   - Files must have correct filename date format

STEP 2: SYSTEM PROCESSES
   - Detects file type (911 or 154) from filename
   - Extracts month/year from date in filename
   - Finds header row automatically
   - Maps columns by name (with positional fallback)
   - Filters for leaf-node accounts only
   - Converts numeric codes (removes .0 float suffix)
   - Strips empty rows (both debit and credit = 0)
   - Deletes previous data for same month/year/file_type (upsert)
   - Stores all valid account entries in pl_entry table

STEP 3: VERIFY IN REPORT
   - Go to /pl/ (P&L Report)
   - Select year from dropdown
   - Table auto-loads with calculated P&L
   - Sub-accounts visible below each main line item

STEP 4: EXPORT (Optional)
   - Click "Export Excel" button
   - Downloads formatted xlsx with:
     * Header row (columns: Chỉ Tiêu | Mã TK | Tháng 1-12 | Tổng Năm)
     * Main line items (bold, colored background)
     * Sub-account rows (separate code column, indented name)
     * Number formatting (thousand separators, negatives in parentheses)


EXCEL EXPORT FORMAT
================================================================================

COLUMN STRUCTURE:
   Column A: Chỉ Tiêu (Line Item / Account Name)
   Column B: Mã TK (Account Code) - Empty for main items, populated for sub-accounts
   Columns C-N: Tháng 1-12 (Monthly values)
   Column O: Tổng Năm (Annual total)

FORMATTING:
   Headers: Bold white text on dark blue background
   Main items: Bold text on light blue background
   Sub-accounts: Regular text on light gray background
   Subtotal rows: Bold text on light green background
   Numbers: Right-aligned, thousand separators, negatives in parentheses
   Borders: Thin borders on all cells

EXAMPLE:
   Chỉ Tiêu                | Mã TK  | Tháng 1    | Tháng 2    | ... | Tổng Năm
   Doanh thu thuần         |        | 100,000,000| 150,000,000| ... |1,200,000,000
       Thuê nhân viên cơ   | 5111   | 50,000,000 | 75,000,000 | ... | 600,000,000
       Lương bộ phận       | 5112   | 50,000,000 | 75,000,000 | ... | 600,000,000
   Giá vốn hàng bán        |        | 500,000,000| 600,000,000| ... |6,000,000,000
       Nguyên vật liệu     | 6211   | 300,000,000| 350,000,000| ... |3,500,000,000
       Công cộng           | 6212   | 200,000,000| 250,000,000| ... |2,500,000,000
   Lợi nhuận gộp           |        |(400,000,000)|(450,000,000)| ... |(4,800,000,000)


DATABASE SCHEMA
================================================================================

TABLE: pl_entry
   id (Integer, Primary Key, Auto-increment)
   source_file (String 255): Original filename
   file_type (String 10): '911' or '154'
   month (Integer): 1-12
   year (Integer): e.g., 2026
   account_code (String 20, Indexed): e.g., "5111"
   account_name (String 255): Account description
   debit (Float): Ps Nợ value
   credit (Float): Ps Có value
   imported_at (DateTime): Import timestamp

INDEXES:
   - account_code (for faster filtering during calculation)

UNIQUE CONSTRAINT: None
   - Multiple entries can exist for same code (across different months/years)
   - Same month/year/file_type/code: Previous entry is deleted on re-import (upsert)

TABLE: account_mapping
   id (Integer, Primary Key, Auto-increment)
   local_code (String 50, Unique, Indexed): Original code
   hq_code (String 50): Target code/description
   created_at (DateTime): Creation timestamp
   updated_at (DateTime): Last update timestamp

UPSERT BEHAVIOR:
   - On import: Check if local_code exists
   - If exists: Update hq_code
   - If not: Insert new row


KNOWN LIMITATIONS & DESIGN NOTES
================================================================================

1. MONTH EXTRACTION
   - Always uses FIRST date found in filename
   - Example: "911 t 01.02.2026-28.02.2026" → Month 2, Year 2026
   - Filename must contain valid date pattern DD.MM.YYYY or DD-MM-YYYY

2. ACCOUNT CODE CONVERSION
   - Excel numeric cells read as floats (e.g., 51131 → 51131.0)
   - System converts to integer string: "51131.0" → "51131"
   - Non-numeric codes preserved (e.g., "5113A" stays "5113A")

3. LEAF-NODE DETECTION
   - Calculated at query time, not at import time
   - Per (month, file_type, prefix_group) combination
   - Allows flexibility: same code can be parent in one month, leaf in another
   - Parent accounts are automatically excluded (never displayed or calculated)

4. COGS FROM "154 t" FILE
   - ALL accounts starting with 6 or 8 in "154 t" file treated as COGS
   - No specific "154x" account code needed
   - File type "154 t" designation indicates cost accounts

5. ZERO HANDLING
   - Rows with both debit and credit = 0 are skipped at import
   - Annual totals of 0 are displayed as "-" in Excel
   - Zero values don't break calculations

6. DUPLICATE HANDLING ON RE-IMPORT
   - Previous data for same (month, year, file_type) is deleted
   - New data inserted
   - Prevents duplicate sub-account rows
   - Safe to re-import with corrections


TROUBLESHOOTING
================================================================================

ISSUE: Import shows success but no records appear
CAUSE: File headers not detected, or all rows filtered as non-leaf accounts
FIX: Check filename format (must have date), verify column headers match spec

ISSUE: Account codes show ".0" suffix in report
CAUSE: Import didn't convert float to integer string
FIX: Manually correct or re-import (system should auto-convert now)

ISSUE: Sub-account total doesn't match main line item
CAUSE: Parent accounts being included, or leaf-node detection issue
FIX: Check for codes where one is prefix of another (hierarchy conflict)

ISSUE: Edit Mapping modal shows no data
CAUSE: mappingsData JS variable was const (immutable)
FIX: Use "let" instead of "const" (should be fixed in current version)

ISSUE: Excel export columns misaligned
CAUSE: Column calculation wrong during Upsert feature addition
FIX: Verify annual_col = get_column_letter(15) for Column O

ISSUE: Google Sheets import fails
CAUSE: Sheet not publicly accessible, or URL format invalid
FIX: Check share settings (Share → Anyone with link), verify URL format


VERSION HISTORY
================================================================================

v1.0 (Current)
- Core P&L calculation engine
- Excel/Google Sheets import
- Sub-account filtering (leaf-node detection)
- Account mapping feature
- Web interface with monthly breakdown
- Excel export with formatting
- Browser table view with sticky columns
- Account code to integer string conversion
- Upsert on re-import (no duplicate accumulation)


TECHNICAL STACK
================================================================================

Backend:
   - Python 3.9+
   - Flask 3.x
   - SQLAlchemy 3.x (ORM)
   - Pandas 2.x (data processing)
   - openpyxl 3.x (Excel generation)

Frontend:
   - HTML5 / Jinja2 templates
   - JavaScript (vanilla, no framework)
   - Tailwind CSS (styling)
   - Bootstrap Icons (iconography)

Database:
   - SQLite (development)
   - PostgreSQL (production)

Deployment:
   - Gunicorn (WSGI server)
   - Railway.app (hosting)


API ENDPOINTS
================================================================================

GET  /pl/                              Dashboard (page)
GET  /pl/import                        Import page (page)

GET  /pl/api/report?year=YYYY         Get P&L data (JSON)
GET  /pl/api/available-years          List years with data
GET  /pl/api/export?year=YYYY         Download Excel export
DELETE /pl/api/delete-all              Clear all P&L data

POST /pl/api/upload/pl-file           Upload Excel file
POST /pl/api/upload/pl-google         Import from Google Sheets

GET  /pl/api/mappings                 Get all mappings
POST /pl/api/mappings/add             Add mapping
DELETE /pl/api/mappings/<code>        Delete mapping
POST /pl/api/mappings/import-excel    Import mappings (Excel)
POST /pl/api/mappings/import-google   Import mappings (Google Sheets)
GET  /pl/api/mappings/export          Export mappings (Excel)


FOR MORE INFORMATION
================================================================================

- Application: /pl/ (P&L Report Dashboard)
- Import Data: /pl/import
- Source Code: app/routes_pl.py, app/services/pl_import.py
- Templates: app/templates/pl/
- Models: app/models/pl_entry.py, app/models/account_mapping.py

================================================================================
                              END OF README
================================================================================
