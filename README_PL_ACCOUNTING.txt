================================================================================
                    OTL P&L REPORT APPLICATION
           Báo cáo Kết quả Hoạt động Kinh doanh (P&L Report)
================================================================================

PROJECT OVERVIEW
================================================================================
The OTL P&L Report application is a specialized financial reporting tool that
processes Vietnamese accounting data (from "911 t", "154 t", and "SDCK 1541"
files) and generates comprehensive Profit & Loss (P&L) statements on a monthly
and annual basis.

The system automatically:
  1. Imports three types of accounting files (911 t, 154 t, SDCK 1541)
  2. Identifies and aggregates financial data by leaf-node account codes
     (excluding parent/summary accounts to prevent double-counting)
  3. Calculates COGS using the inventory formula: Production Costs + Inventory
     Adjustment (SDCK)
  4. Computes all P&L metrics following standard Vietnamese accounting principles


SYSTEM REQUIREMENTS
================================================================================

1. FILE INPUT FORMATS
   - Excel files (.xlsx, .xls)
   - Google Sheets (publicly accessible links)

2. SUPPORTED FILE TYPES (THREE REQUIRED)

   File 1: "911 t" (P&L Aggregation)
   - Purpose: Contains main revenue and operating expense accounts
   - Source: Monthly P&L statement from accounting system
   - Accounts: 5xx (revenue), 6xx (production costs), 8xx (cost adjustments),
              642x (operating expenses), 635x (finance costs), 711x/811x (other income/expenses)
   - Columns: Tk đ.ứng (code), Tên tk đ.ứng (name), Ps nợ (debit), Ps có (credit)

   File 2: "154 t" (Cost of Production)
   - Purpose: Contains detailed production/manufacturing cost accounts (6xx only)
   - Source: Cost accounting report from production department
   - Accounts: 6xx only (raw materials, direct labor, manufacturing overhead)
   - Use: Aggregated as COGS (Giá vốn hàng bán)
   - Columns: Tk đ.ứng (code), Tên tk đ.ứng (name), Ps nợ (debit), Ps có (credit)

   File 3: "SDCK 1541" (Số dư cuối kỳ - Ending Balance)
   - Purpose: Ending inventory balance adjustment for COGS calculation
   - Source: Inventory reconciliation at month-end
   - Account: 1541 (Inventory account)
   - Use: Added to COGS formula as inventory adjustment
   - Columns: Tk (code), Tên tk (name), Ps nợ (debit - the ending balance)
   - Formula: COGS = Sum(6xx from 154 t) + SDCK 1541 (negative adjustment)

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
   - 6xx (File: 154 t) → Giá vốn hàng bán (COGS)
     * Base COGS from production costs only (6xx)
     * [Use: Ps Nợ (Debit)]
     * Plus: SDCK 1541 ending inventory adjustment
   - 642x (File: 911 t) → Chi phí QLDN (Operating Expenses)  [Use: Ps Nợ]
   - 635x (File: 911 t) → Chi phí tài chính (Finance Costs)  [Use: Ps Nợ]
   - 811x (File: 911 t) → Chi phí khác (Other Expenses)      [Use: Ps Nợ]


STEP 2: HANDLE THREE FILE TYPES

   File "911 t" Processing:
   - Filter accounts by prefix: 511x, 515x, 642x, 635x, 711x, 811x
   - Identify leaf nodes for each prefix group
   - Use Ps Có (credit) for revenue accounts (511x, 515x, 711x)
   - Use Ps Nợ (debit) for expense accounts (642x, 635x, 811x)

   File "154 t" Processing:
   - Filter accounts by prefix: 6xx only (production costs)
   - Identify leaf nodes (accounts with no children)
   - Use Ps Nợ (debit) - cost accounts
   - Aggregate as single "Giá vốn hàng bán" line item
   - Note: 8xx accounts are NOT included in 154 t file

   File "SDCK 1541" Processing:
   - Extract account codes and ending balance amounts
   - Convert balance to negative (inventory adjustment)
   - Add DIRECTLY to COGS total (not as sub-account breakdown)
   - Example: SDCK balance of 300,000 → adds -300,000 to COGS

STEP 2B: AGGREGATE LEAF-NODE AMOUNTS

   For each (month, file_type, account_prefix) group:
   1. Identify all accounts from file
   2. Calculate leaf nodes (accounts with no children)
   3. Sum ONLY leaf-node values, NOT parent account totals
   4. For SDCK: Simply add adjustment value to COGS total


STEP 3: CALCULATE P&L LINE ITEMS (Sequential)

   Line 1: Doanh thu thuần (Net Revenue)
   = Sum of Ps Có from all leaf codes starting with 511x

   Line 2: Giá vốn hàng bán (Cost of Goods Sold - COGS)

   Formula: COGS = Production Costs (154 t) + SDCK Adjustment (1541)

   Step A: Sum Production Costs from "154 t" file
   = Sum of Ps Nợ (debit) from all LEAF codes starting with 6xx ONLY

   Example of "154 t" accounts (leaf nodes only):
   - 6211 (Raw Materials): 1,000,000
   - 6221 (Direct Labor): 500,000
   - 6231 (Manufacturing Overhead): 200,000
   - 6241 (Factory Utilities): 100,000
   - Subtotal: 1,800,000

   Note: 154 t file contains ONLY 6xx accounts (no 8xx)

   Step B: Add SDCK 1541 Ending Inventory Adjustment
   = SDCK balance from pl_sdck table (already stored as NEGATIVE)

   Example of SDCK processing:
   - File "SDCK 1541 28.02.2026.xlsx" contains:
     * 154101 (Raw Materials on hand): 400,000
     * 154102 (Work in Progress): 100,000
     * 154103 (Finished Goods): 300,000
     * Total: 800,000 → Stored as: -800,000

   Final COGS Calculation:
   = 1,800,000 (Production Costs) + (-800,000) (SDCK Adjustment)
   = 1,000,000 (Final COGS)

   Accounting Logic:
   - Production Costs (154 t) = Direct costs incurred during period
   - SDCK Adjustment (negative) = Ending inventory value subtracted
   - Result = Actual cost of goods SOLD (not on hand)

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


DETAILED COGS (Giá vốn hàng bán) EXPLANATION
================================================================================

DEFINITION:
   Giá vốn hàng bán (COGS) = Cost of Goods Sold
   - The actual cost of products sold during the accounting period
   - Distinguishes between costs incurred vs. costs of inventory on hand
   - Critical for calculating Gross Profit (Revenue - COGS)

ACCOUNTING FORMULA (Vietnamese Standard):
   COGS = Opening Inventory + Production Costs - Ending Inventory
   Or:
   COGS = Production Costs - (Ending Inventory - Opening Inventory)
   Or:
   COGS = Sum of 154t (6xx costs) + SDCK 1541 (inventory adjustment)

WHY THREE FILE TYPES?

   File "154 t" (TK 154 t - TK 6xx):
   ────────────────────────────────
   - Contains production costs INCURRED during the period
   - Accounts 6xx = Raw materials, direct labor, manufacturing overhead
   - Note: 8xx accounts are NOT included in 154 t file
   - Represents actual EXPENDITURE on production
   - Use Ps Nợ (debit side) values only
   - Example:
     * 6211 (Raw Materials): 1,000,000
     * 6221 (Direct Labor): 500,000
     * 6231 (Manufacturing Overhead): 100,000
     * Subtotal: 1,600,000

   File "SDCK 1541" (Số dư cuối kỳ - Ending Inventory):
   ────────────────────────────────────────────────────
   - Contains ending balance of inventory account 1541
   - Represents physical inventory VALUE on hand at month-end
   - Accounts 154101, 154102, 154103 = Categories of inventory
   - Stored as NEGATIVE to represent subtraction from COGS
   - Example:
     * 154101 (Raw Materials on hand): 400,000 → -400,000
     * 154102 (Work in Progress): 100,000 → -100,000
     * 154103 (Finished Goods): 300,000 → -300,000
     * Subtotal: 800,000 → Stored as -800,000

   File "911 t" (DOES NOT contain COGS accounts):
   ──────────────────────────────────────────────
   - Contains only revenue and operating expenses
   - 511x = Revenue, 515x = Financial revenue, 711x = Other income
   - 642x = Operating expenses, 635x = Finance costs, 811x = Other expenses
   - DOES NOT contain production costs (6xx)
   - Note: All 8xx accounts are cost adjustments, not in 154 t
   - COGS is NOT calculated from 911 t file

LEAF-NODE FILTERING FOR COGS:

   Raw 154 t File Content (6xx ONLY):
   ├── 6 (parent - EXCLUDED)
   │  ├── 62 (parent - EXCLUDED)
   │  │  ├── 621 (parent - EXCLUDED)
   │  │  │  ├── 6211 (LEAF - INCLUDED) ✓
   │  │  │  └── 6212 (LEAF - INCLUDED) ✓
   │  │  └── 622 (parent - EXCLUDED)
   │  │     └── 6221 (LEAF - INCLUDED) ✓
   │  ├── 63 (parent - EXCLUDED)
   │  │  └── 631 (LEAF - INCLUDED) ✓
   │  └── 64 (parent - EXCLUDED)
   │     └── 641 (LEAF - INCLUDED) ✓

   Note: 8xx accounts are NOT in 154 t file

   Algorithm per month:
   1. Collect ALL codes starting with 6 or 8 from 154 t
   2. Identify leaf codes (codes with no children)
   3. Sum ONLY leaf codes' debit values
   4. Ignore parent accounts (they aggregate children)

STEP-BY-STEP COGS CALCULATION:

   Step 1: Get Production Costs from 154 t (6xx Leaf Codes Only)
   ─────────────────────────────────────────────────────────────
   SELECT SUM(debit)
   FROM pl_entry
   WHERE year = 2026
     AND month = 2
     AND file_type = '154'
     AND account_code IN (SELECT leaf_codes for prefix 6)

   Example result: 1,600,000 (sum of all 6xx leaf codes)
   Note: 8xx accounts are not included in 154 t file

   Step 2: Get SDCK Ending Inventory Adjustment
   ──────────────────────────────────────────
   SELECT SUM(balance)  -- Already stored as NEGATIVE
   FROM pl_sdck
   WHERE year = 2026
     AND month = 2
     AND account_target = '1541'

   Example result: -800,000 (already negative)

   Step 3: Add Both Components
   ─────────────────────────
   COGS = 1,600,000 + (-800,000) = 800,000

WHAT EACH COMPONENT MEANS:

   Production Costs (1,600,000):
   - Money spent on raw materials, labor, factory overhead
   - Actual CASH or EXPENSE incurred
   - All costs for goods that will be/were sold

   SDCK Adjustment (-800,000):
   - Value of goods still on hand (inventory)
   - These goods were NOT SOLD yet
   - So subtract them from production costs
   - Next month: this becomes "opening inventory"

   Final COGS (800,000):
   - Cost of goods that were ACTUALLY SOLD
   - = Production costs - unsold inventory
   - Used to calculate Gross Profit = Revenue - COGS

EXAMPLE WITH REAL NUMBERS:

   Scenario:
   - Opening Inventory (Jan 1): 500,000 (from previous month's SDCK)
   - Production Costs in February: 1,600,000 (from 154 t file)
   - Goods Available for Sale: 500,000 + 1,600,000 = 2,100,000
   - Ending Inventory (Feb 28): 800,000 (from SDCK 1541)
   - COGS (what was sold): 2,100,000 - 800,000 = 1,300,000

   System Calculation (simplified):
   - COGS = Production Costs + SDCK
   - COGS = 1,600,000 + (-800,000) = 800,000
   - Note: The system doesn't require opening inventory because:
     * SDCK stores the running inventory balance
     * Each month's SDCK becomes next month's opening inventory
     * The adjustment is automatic through accumulated SDCK

COMMON MISTAKES:

   ❌ MISTAKE: Using accounts from 911 t file for COGS
   ✓ CORRECT: COGS comes ONLY from 154 t (6xx only) + SDCK

   ❌ MISTAKE: Including parent codes (6, 62, 621)
   ✓ CORRECT: Include ONLY leaf codes (6211, 6212, 6221, etc.)

   ❌ MISTAKE: Forgetting SDCK adjustment
   ✓ CORRECT: COGS = 154 t total + SDCK (which is negative)

   ❌ MISTAKE: Using positive SDCK value
   ✓ CORRECT: SDCK is stored and used as NEGATIVE

   ❌ MISTAKE: Summing parent account amounts
   ✓ CORRECT: Parent accounts are aggregates; sum only leaves


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

STEP 1: UPLOAD THREE FILES
   - Go to /pl/import → "Import Data" section
   - Upload all three file types:
     * "911 t" (P&L Aggregation) - required for revenue/expenses
     * "154 t" (Cost of Production) - required for COGS base
     * "SDCK 1541" (Ending Inventory) - required for COGS adjustment
   - Can upload as Excel files (.xlsx, .xls) or paste Google Sheets URLs
   - All files must have valid filename date format

STEP 2: SYSTEM PROCESSES EACH FILE TYPE

   For "911 t" files:
   - Detects file type from filename
   - Extracts month/year from date in filename
   - Finds header row automatically
   - Maps columns by name (case-insensitive with positional fallback)
   - Filters for leaf-node accounts only per prefix group
   - Converts numeric codes (removes .0 float suffix)
   - Strips empty rows (both debit and credit = 0)
   - Deletes previous data for same month/year (upsert)
   - Stores valid entries in pl_entry table with file_type='911'

   For "154 t" files:
   - Same process as 911 t
   - Identifies accounts starting with 6 or 8
   - Filters for leaf nodes (accounts with no children)
   - All debit values contribute to COGS calculation
   - Stores in pl_entry table with file_type='154'

   For "SDCK 1541" files:
   - Detects file type from "SDCK 1541" in filename
   - Extracts account_target = "1541"
   - Reads account codes, names, and ending balances
   - Converts balances to NEGATIVE (for formula: costs - inventory)
   - Stores in pl_sdck table (separate from pl_entry)
   - Does NOT perform leaf-node filtering
   - Each sub-account balance stored individually

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


SDCK CALCULATION DETAILS
================================================================================

WHAT IS SDCK?
   SDCK = Số dư cuối kỳ (Ending Balance)
   - Month-end balance of inventory account (1541)
   - Represents the value of goods on hand at period close
   - Used to adjust COGS in Vietnamese accounting

WHY IS SDCK NEEDED?
   Vietnamese COGS formula follows the inventory adjustment method:

   COGS = Opening Inventory + Production Costs - Ending Inventory (SDCK)

   Example with January data:
   - Opening Inventory (Jan 1): 500,000
   - Production Costs (154 t): 2,000,000
   - Ending Inventory (SDCK Jan 31): 300,000
   - COGS = 500,000 + 2,000,000 - 300,000 = 2,200,000

HOW SDCK DATA IS STRUCTURED

   SDCK File Format:
   - Filename: "SDCK 1541 28.02.2026.xlsx"
   - Contains: Ending balance of all sub-accounts under 1541
   - Date: Month-end date of the period

   Example SDCK File Columns:
   | Tk (Code) | Tên tk (Name)        | Ps nợ (Balance) |
   | 154101    | Raw Materials        | 300,000         |
   | 154102    | Work in Progress     | 100,000         |
   | 154103    | Finished Goods       | 200,000         |
   | (TOTAL)   |                      | 600,000         |

HOW SDCK IS PROCESSED

   Step 1: Extract from File
   - Read each row: account code, account name, balance amount
   - Extract month/year from filename date (e.g., 28.02.2026 → Month 2)
   - Store with account_target = "1541"

   Step 2: Convert to Negative
   - Original balance: 600,000 (debit side representation)
   - System converts: balance = -float(600,000) = -600,000
   - Reason: In COGS formula, ending inventory is SUBTRACTED
   - Formula: COGS = Production Costs - Ending Inventory = Costs + (-Inventory)

   Step 3: Add to COGS Total
   - Query all SDCK entries for the year
   - For each month, add SDCK balance to "Giá vốn hàng bán" total
   - Example:
     * Production Costs (154 t): 2,000,000
     * SDCK adjustment: -300,000 (stored as negative)
     * Final COGS: 2,000,000 + (-300,000) = 1,700,000

DATABASE STORAGE
   Table: pl_sdck
   - source_file: "SDCK 1541 28.02.2026.xlsx"
   - account_target: "1541"
   - month: 2
   - year: 2026
   - account_code: "154101" (sub-account under 1541)
   - account_name: "Raw Materials"
   - balance: -300000 (stored as negative for calculation)

EXAMPLE: COMPLETE COGS CALCULATION

   Given:
   - 154 t file (Feb 2026) contains:
     * Account 6211 (Materials): 1,000,000 (Ps nợ)
     * Account 6221 (Labor): 500,000 (Ps nợ)
     * Account 8111 (Factory OH): 200,000 (Ps nợ)

   - SDCK 1541 file (28.02.2026) contains:
     * Total inventory: 400,000

   Calculation:
   1. Sum leaf accounts from 154 t: 1,000,000 + 500,000 + 200,000 = 1,700,000
   2. Add SDCK adjustment: 1,700,000 + (-400,000) = 1,300,000
   3. Final COGS = 1,300,000

IMPORTANT NOTES

   ✓ SDCK is OPTIONAL if ending inventory is zero
   ✓ SDCK balance is stored as NEGATIVE to align with formula
   ✓ Multiple SDCK entries per month (sub-accounts) are summed together
   ✓ SDCK accounts (e.g., 154101, 154102) are NOT displayed as P&L sub-accounts
     (they are aggregated into the single COGS adjustment)
   ✓ If no SDCK file is imported, COGS = Sum of 154 t file only (no adjustment)


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

TABLE: pl_sdck
   id (Integer, Primary Key, Auto-increment)
   source_file (String 255): Original filename (e.g., "SDCK 1541 28.02.2026.xlsx")
   account_target (String 10): Target account code (e.g., "1541")
   month (Integer): 1-12
   year (Integer): e.g., 2026
   account_code (String 20, Indexed): Sub-account code (e.g., "154101")
   account_name (String 255): Sub-account description
   balance (Float): Ending balance (stored as NEGATIVE for calculation)
   imported_at (DateTime): Import timestamp

RELATIONSHIP TO COGS:
   - All SDCK entries for a given month are summed
   - The total is added to COGS line item automatically
   - Not displayed as individual sub-account rows

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

4. COGS CALCULATION (FROM "154 t" + SDCK)
   - Base COGS: ALL accounts starting with 6 or 8 in "154 t" file
   - Adjustment: SDCK 1541 ending inventory (stored as negative)
   - Final COGS = Sum of leaf codes in 154 t + SDCK adjustment
   - No specific "154x" account code needed
   - File type "154 t" designation indicates cost accounts

5. SDCK FILE REQUIREMENTS
   - Filename must contain "SDCK 1541" and valid date (DD.MM.YYYY)
   - Example: "SDCK 1541 28.02.2026.xlsx"
   - Columns: Tk (code), Tên tk (name), Ps nợ (balance)
   - Balance stored as negative for calculation
   - Optional: If no SDCK imported, COGS = 154 t only (no adjustment)

6. ZERO HANDLING
   - Rows with both debit and credit = 0 are skipped at import
   - SDCK rows with balance = 0 are skipped
   - Annual totals of 0 are displayed as "-" in Excel
   - Zero values don't break calculations

7. DUPLICATE HANDLING ON RE-IMPORT
   - Previous data for same (month, year, file_type) is deleted
   - New data inserted
   - SDCK data for same (month, year, account_target) is replaced
   - Prevents duplicate sub-account rows
   - Safe to re-import with corrections

8. THREE FILE TYPES INDEPENDENCE
   - Each file type is imported separately (can upload in any order)
   - 911 t and 154 t share same pl_entry table (different file_type)
   - SDCK uses separate pl_sdck table
   - Can update one file type without re-uploading others
   - System handles missing files gracefully:
     * Missing 911 t: P&L lines without 911 data = 0
     * Missing 154 t: COGS = SDCK adjustment only
     * Missing SDCK: COGS = 154 t total (no inventory adjustment)


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

ISSUE: COGS value seems incorrect or doesn't match expected
CAUSE: Missing SDCK file, or SDCK balance is wrong
FIX: Verify SDCK 1541 file is imported. Check ending inventory balance.
     COGS = 154 t total + SDCK (negative), not just 154 t alone.

ISSUE: SDCK import shows "already exists" errors
CAUSE: SDCK file imported twice with same month/year
FIX: System performs upsert on SDCK. Check database for duplicate entries.
     Safe to re-import with corrected balance values.

ISSUE: Different COGS value between web report and Excel export
CAUSE: Timing issue or unsaved SDCK data
FIX: Ensure all three files (911t, 154t, SDCK) are fully imported.
     Wait for import confirmation before generating export.
     Refresh browser and re-generate export.


VERSION HISTORY
================================================================================

v1.0 (Current)
- Core P&L calculation engine with three file types:
  * 911 t (Revenue & Operating Expenses)
  * 154 t (Production Costs)
  * SDCK 1541 (Inventory Adjustment for COGS)
- COGS formula: Production Costs (154 t) + Inventory Adjustment (SDCK)
- Excel/Google Sheets import for all three file types
- Sub-account filtering (leaf-node detection)
- Account mapping feature
- Web interface with monthly breakdown
- Excel export with formatting
- Browser table view with sticky columns
- Account code to integer string conversion (removes .0 suffix)
- Upsert on re-import (no duplicate accumulation)
- Separate storage: pl_entry (911t/154t), pl_sdck (inventory balances)
- Auto-detection of file type from filename
- Graceful handling of missing files


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
- Import Data: /pl/import (upload 911t, 154t, SDCK 1541 files)
- Source Code: app/routes_pl.py, app/services/pl_import.py
- Templates: app/templates/pl/
- Models:
  * app/models/pl_entry.py (stores 911t and 154t data)
  * app/models/pl_sdck.py (stores inventory ending balances)
  * app/models/account_mapping.py (stores local→HQ code mappings)

QUICK START CHECKLIST
================================================================================

1. ☐ Prepare three Excel files:
   - "911 t 01.02.2026-28.02.2026.xlsx" (P&L data)
   - "154 t 01.02.2026-28.02.2026.xlsx" (Production costs)
   - "SDCK 1541 28.02.2026.xlsx" (Ending inventory)

2. ☐ Verify columns in each file:
   - 911t/154t: Tk đ.ứng | Tên tk đ.ứng | Ps nợ | Ps có
   - SDCK: Tk | Tên tk | Ps nợ

3. ☐ Upload all files via /pl/import → Import Data
   - Supports batch upload
   - Can upload individually in any order

4. ☐ Go to /pl/ → Select year → View P&L Report
   - Verify main line items and sub-accounts appear
   - Check COGS includes both 154t costs and SDCK adjustment

5. ☐ Export to Excel (optional)
   - Click "Export Excel" button
   - Downloads formatted .xlsx with all data

================================================================================
                              END OF README
================================================================================
