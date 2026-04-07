# OTL MyApps - Financial Management Platform

A comprehensive financial management system with two main modules:

## 📊 Module 1: OTL Reports (Invoice & Booking Dashboard)

**Documentation:** [`README_OTL_REPORTS.txt`](README_OTL_REPORTS.txt)

Business intelligence dashboard for tracking invoices and bookings with:
- Real-time KPIs (Total Revenue, Tax, Customers, Bookings)
- Interactive dashboards with charts and visualizations
- Revenue analysis by Month, Category, Routes, Customers
- Advanced filtering (Month, Category, Currency selector)
- Search and pagination across 35+ data columns
- Export to Excel functionality
- Full audit trail (Created By, Last Modified)

**Key Features:**
- Multiple currency support (Local + Foreign currencies)
- FTL/LTL booking categorization
- Top 10 routes and customers ranking
- Invoice status tracking

---

## 📈 Module 2: PL Accounting (P&L Financial Statements)

**Documentation:** [`README_PL_ACCOUNTING.txt`](README_PL_ACCOUNTING.txt)

Specialized Vietnamese accounting module for generating Profit & Loss statements with:
- Three-file import system:
  - **911 t** — P&L aggregation (Revenue & Operating Expenses)
  - **154 t** — Cost of Production (Manufacturing Costs)
  - **SDCK 1541** — Ending Inventory Balance (COGS Adjustment)
- Automatic leaf-node filtering (prevents double-counting)
- COGS calculation with inventory adjustment formula
- 10-line P&L statement with subtotals
- Sub-account breakdown in both web and Excel formats
- Monthly and annual reporting

**Key Features:**
- Inventory adjustment formula: `COGS = Production Costs + SDCK Adjustment`
- Smart leaf-node detection for hierarchical accounts
- Detailed sub-account reporting with separate code column
- Professional Excel export with formatting
- Support for Excel and Google Sheets import

---

## 🗂️ File Organization

```
/Users/nguyenlinh/DEV/MyApps/
├── README.md                          ← This file (overview)
├── README_OTL_REPORTS.txt             ← Invoice/Booking module docs
├── README_PL_ACCOUNTING.txt           ← P&L Accounting module docs
│
├── app/
│   ├── routes_otl.py                  ← OTL Reports routes
│   ├── routes_pl.py                   ← P&L Accounting routes
│   │
│   ├── services/
│   │   ├── otl_service.py             ← OTL business logic
│   │   └── pl_import.py               ← P&L import/calculation logic
│   │
│   ├── models/
│   │   ├── invoice.py                 ← Invoice model (OTL)
│   │   ├── pl_entry.py                ← P&L entry model
│   │   └── pl_sdck.py                 ← Inventory balance model
│   │
│   └── templates/
│       ├── otl/                       ← OTL Reports UI
│       └── pl/                        ← P&L Accounting UI
│
└── ...
```

---

## 🚀 Quick Start

### For OTL Reports (Invoice Dashboard):
1. Import invoice booking data via Excel or Google Sheets
2. Go to `/otl/` dashboard
3. Use filters (Month, Category, Currency) to view KPIs
4. Export reports to Excel

**See:** [`README_OTL_REPORTS.txt`](README_OTL_REPORTS.txt)

### For P&L Accounting:
1. Prepare three files:
   - `911 t 01.02.2026-28.02.2026.xlsx` (P&L data)
   - `154 t 01.02.2026-28.02.2026.xlsx` (Production costs)
   - `SDCK 1541 28.02.2026.xlsx` (Ending inventory)
2. Upload via `/pl/import` page
3. Go to `/pl/` to view P&L statement
4. Export to Excel

**See:** [`README_PL_ACCOUNTING.txt`](README_PL_ACCOUNTING.txt)

---

## 📋 Key Differences

| Feature | OTL Reports | PL Accounting |
|---------|-------------|---------------|
| **Purpose** | Business dashboard | Financial statements |
| **Data** | Invoices & bookings | Accounting entries |
| **Files** | Invoice booking data | 911t, 154t, SDCK 1541 |
| **Key Metric** | Revenue & KPIs | P&L statement |
| **Audience** | Operations/Sales | Finance/Accounting |
| **Currency** | Multi-currency support | Vietnamese accounting |
| **Export** | Excel with KPIs | Excel with P&L statement |

---

## 🔧 Technical Stack

**Backend:**
- Python 3.9+ / Flask 3.x
- SQLAlchemy ORM
- Pandas (data processing)
- openpyxl (Excel generation)

**Frontend:**
- HTML5 / Jinja2 templates
- JavaScript (vanilla)
- Tailwind CSS / Bootstrap Icons

**Database:**
- SQLite (development)
- PostgreSQL (production)

---

## 📞 For More Information

- **OTL Reports Module:** See [`README_OTL_REPORTS.txt`](README_OTL_REPORTS.txt)
- **P&L Accounting Module:** See [`README_PL_ACCOUNTING.txt`](README_PL_ACCOUNTING.txt)
- **Source Code:** `app/routes_*.py`, `app/services/*.py`
- **Models:** `app/models/`
- **Templates:** `app/templates/`

---

**Last Updated:** April 6, 2026
**Version:** 1.0
