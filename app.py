
# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title="College Mess Bill Calculator", page_icon="🍽️", layout="centered")
st.title("🍽️ College Mess Bill Calculator")

# --- Session State for dynamic fixed expenses ---
if "fixed_items" not in st.session_state:
    st.session_state.fixed_items = []  # list of dicts: {name, amount}

# --- Period / Month ---
st.subheader("Select Billing Period")
colp1, colp2 = st.columns(2)
with colp1:
    billing_month = st.selectbox("Month", list(range(1,13)), index=date.today().month-1, format_func=lambda m: date(2000,m,1).strftime("%B"))
with colp2:
    billing_year = st.number_input("Year", min_value=2000, max_value=2100, value=date.today().year, step=1)

st.divider()

# --- Upload Invoices ---
st.subheader("Step 1: Upload Invoices")
st.caption("Upload CSV or Excel files. Expected columns: **Amount** (required), optional **Item** and **Category**. Examples: grocery, vegetables, fruits, eggs, gas.")
uploads = st.file_uploader("Upload one or more invoice files", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

all_invoices = []
invoice_totals = []

def read_table(file):
    import pandas as pd
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    # Normalize columns
    cols = {c.strip().lower(): c for c in df.columns}
    # Ensure Amount column exists (case-insensitive)
    amount_col = None
    for c in df.columns:
        if c.strip().lower() == "amount":
            amount_col = c
            break
    if amount_col is None:
        # try common alternatives
        for alt in ["total","price","value","amt"]:
            if alt in cols:
                amount_col = cols[alt]
                break
    if amount_col is None:
        st.error(f"❌ {file.name}: could not find an 'Amount' column.")
        return None
    # Optional columns
    item_col = None
    for c in df.columns:
        if c.strip().lower() in ["item","description","particulars","name"]:
            item_col = c
            break
    category_col = None
    for c in df.columns:
        if c.strip().lower() in ["category","type","group"]:
            category_col = c
            break

    # Build normalized frame
    out = pd.DataFrame()
    out["Item"] = df[item_col] if item_col else ""
    out["Category"] = df[category_col] if category_col else ""
    out["Amount"] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)
    return out

total_invoice_amount = 0.0
if uploads:
    for f in uploads:
        df = read_table(f)
        if df is not None:
            all_invoices.append(df.assign(Source=f.name))
            inv_total = df["Amount"].sum()
            invoice_totals.append({"File": f.name, "Total": inv_total})
            total_invoice_amount += inv_total

    if all_invoices:
        invoices_df = pd.concat(all_invoices, ignore_index=True)
        with st.expander("Preview combined invoice lines"):
            st.dataframe(invoices_df, use_container_width=True)
        if invoice_totals:
            st.write("**Per-file totals**")
            st.dataframe(pd.DataFrame(invoice_totals))
else:
    invoices_df = pd.DataFrame(columns=["Item","Category","Amount","Source"])

st.write(f"**Total Invoice Amount:** ₹{total_invoice_amount:,.2f}")

st.divider()

# --- Fixed Expenses ---
st.subheader("Step 2: Fixed Expenses")
c1, c2, c3 = st.columns(3)
with c1:
    cook_salary = st.number_input("Cook salary (₹)", min_value=0.0, value=0.0, step=100.0)
with c2:
    helpers_salary = st.number_input("Helpers salary (₹)", min_value=0.0, value=0.0, step=100.0)
with c3:
    caretaker_salary = st.number_input("Caretaker salary (₹)", min_value=0.0, value=0.0, step=100.0)

# Custom fixed expense adder
with st.expander("Add more fixed expenses (e.g., rent, maintenance, gas if not invoiced)"):
    name = st.text_input("Expense name", key="fx_name")
    amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=100.0, key="fx_amount")
    add = st.button("➕ Add fixed expense")
    if add and name and amount > 0:
        st.session_state.fixed_items.append({"name": name, "amount": float(amount)})
    if st.session_state.fixed_items:
        fx_df = pd.DataFrame(st.session_state.fixed_items)
        st.dataframe(fx_df.rename(columns={"name":"Name","amount":"Amount"}), use_container_width=True)
        if st.button("Clear added fixed expenses"):
            st.session_state.fixed_items = []

fixed_expenses = cook_salary + helpers_salary + caretaker_salary + sum([x["amount"] for x in st.session_state.fixed_items])
st.write(f"**Total Fixed Expenses:** ₹{fixed_expenses:,.2f}")

st.divider()

# --- Students ---
st.subheader("Step 3: Students")
coln1, coln2 = st.columns(2)
with coln1:
    num_students = st.number_input("Number of students", min_value=1, value=50, step=1)
with coln2:
    decimals = st.selectbox("Rounding for per-student bill", options=[0, 1, 2], index=0, help="Round to nearest rupees or paise")

# --- Calculations ---
total_expenses = float(total_invoice_amount) + float(fixed_expenses)
per_student = round(total_expenses / num_students, int(decimals))

st.divider()
st.subheader("📊 Summary")
st.write(f"Billing Period: **{date(billing_year, billing_month, 1).strftime('%B %Y')}**")
st.metric("Total Invoices", f"₹{total_invoice_amount:,.2f}")
st.metric("Total Fixed", f"₹{fixed_expenses:,.2f}")
st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
st.metric("Per Student", f"₹{per_student:,.{decimals}f}")

# Breakdown tables
with st.expander("Breakdown tables"):
    # Fixed expense table
    base_fixed = [
        {"Name":"Cook salary","Amount": cook_salary},
        {"Name":"Helpers salary","Amount": helpers_salary},
        {"Name":"Caretaker salary","Amount": caretaker_salary},
    ] + [{"Name": x["name"], "Amount": x["amount"]} for x in st.session_state.fixed_items]
    fixed_df = pd.DataFrame(base_fixed)
    st.write("**Fixed Expenses**")
    st.dataframe(fixed_df, use_container_width=True)

    if not invoices_df.empty:
        st.write("**Invoices (grouped by Category)**")
        cat = invoices_df.copy()
        if "Category" in cat.columns:
            grp = cat.groupby(cat["Category"].replace("", "Unspecified"))["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
        else:
            grp = pd.DataFrame({"Category":["All"],"Amount":[total_invoice_amount]})
        st.dataframe(grp, use_container_width=True)

# --- Downloads ---
st.subheader("⬇️ Export")
# Summary CSV
summary = pd.DataFrame({
    "Billing Month":[date(billing_year, billing_month, 1).strftime('%B %Y')],
    "Total Invoice Amount":[total_invoice_amount],
    "Total Fixed Expenses":[fixed_expenses],
    "Total Mess Expenses":[total_expenses],
    "Number of Students":[num_students],
    "Per Student Bill":[per_student]
})

csv_buf = BytesIO()
summary.to_csv(csv_buf, index=False)
st.download_button("Download summary CSV", csv_buf.getvalue(), file_name="mess_bill_summary.csv", mime="text/csv")

# Per-student ledger CSV (equal share)
ledger = pd.DataFrame({
    "Roll No": list(range(1, int(num_students)+1)),
    "Bill Amount": [per_student]*int(num_students)
})
ledger_buf = BytesIO()
ledger.to_csv(ledger_buf, index=False)
st.download_button("Download per-student ledger CSV", ledger_buf.getvalue(), file_name="per_student_ledger.csv", mime="text/csv")

st.caption("Tip: Save this app as a GitHub repo and deploy on Streamlit Community Cloud for free.")
