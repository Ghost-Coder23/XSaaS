# Move Features: Headmaster → Admin Dashboard

## Goal
Move **Fee Management** (invoicing, payment capture, reconciliation) and **Enrollment/Admissions** (adding students, generating admission numbers) from the Headmaster dashboard to the School Admin dashboard.

## Files Edited

### 1. `analytics/views.py` ✅
- **headmaster_dashboard()**: Removed unused management context (teachers/students/subjects/class_sections). Kept finance summary as read-only overview.
- **admin_dashboard()**: Added `partial_invoices`, `overdue_invoices`, `recent_payments`, `pending_payments_count` to context.

### 2. `templates/analytics/dashboard_headmaster.html` ✅
- Removed "Fee Overview" quick action button from Quick Actions card.
- Finance Health card remains as read-only summary for headmaster visibility.

### 3. `templates/analytics/dashboard_admin.html` ✅
- Enhanced Fee Summary card with Partial invoices, Overdue invoices, and Pending Reconciliation metrics.
- Added Quick Actions row with 6 buttons:
  - Enroll Student (`academics:student_add`)
  - Add Teacher (`academics:teacher_add`)
  - Create Invoice (`fees:create_invoice`)
  - Bulk Invoices (`fees:bulk_invoice`)
  - Record Payment (`fees:invoice_list`)
  - Payment Config (`fees:payment_config`)
- Added "Recent Payments" table alongside Recent Invoices and Students Per Class.

### 4. `templates/schools/dashboard_headmaster.html` (legacy) ✅
- Removed "Add Student" quick action button.

### 5. `templates/schools/dashboard_admin.html` (legacy) ✅
- Replaced generic "Manage Fees" with specific fee actions:
  - Create Invoice, Bulk Invoices, Record Payment, Payment Config
- Kept "Enroll Student" as primary action.

## Verification
- `python manage.py check` → System check identified no issues (0 silenced).

## Result
- Headmaster dashboard is now focused on leadership oversight (approvals, analytics, attendance, announcements) with read-only finance visibility.
- Admin dashboard is now the operations command center with full fee management, invoicing, payment reconciliation, and student enrollment capabilities.

