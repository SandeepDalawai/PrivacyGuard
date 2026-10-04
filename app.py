# ============================================================
# PRIVACY-PRESERVING DATA MASKING SYSTEM
# ============================================================
#
# Dataset   : Student Dataset DP A1.xlsx
# Records   : 25 students
# Attributes: Student ID, Age, Gender, PIN Code,
#             Department, CGPA, Scholarship
#
# Desktop UI : Tkinter
# Input      : Excel dataset (.xlsx / .xls)
# Output     : Masked Excel dataset
#
# NON-PERTURBATIVE:
#   1. Suppression
#   2. Generalization
#   3. Top/Bottom Coding
#   4. Aggregation
#
# PERTURBATIVE:
#   5. Noise Addition
#   6. Data Swapping
#   7. Differential Privacy
#   8. Synthetic Data
#
# Run:
#   python app.py
#
# Install:
#   python -m pip install pandas numpy openpyxl
#
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np


# ============================================================
# CENTRALIZED DATASET CONFIGURATION
# ============================================================
# Internal names use underscores; display names use spaces.
# One mapping governs the entire application consistently.
# ============================================================

# Excel column  ->  internal column
COLUMN_RENAME_MAP = {
    "Student ID":  "Student_ID",
    "Age":         "Age",
    "Gender":      "Gender",
    "PIN Code":    "PIN_Code",
    "Department":  "Department",
    "CGPA":        "CGPA",
    "Scholarship": "Scholarship",
}

REQUIRED_COLUMNS = list(COLUMN_RENAME_MAP.values())

# Internal column  ->  human-friendly display name
DISPLAY_NAME_MAP = {v: k for k, v in COLUMN_RENAME_MAP.items()}


# ============================================================
# CENTRALIZED ATTRIBUTE METADATA
# ============================================================

ATTRIBUTE_METADATA = {
    "Student_ID": {
        "display_name":           "Student ID",
        "data_type":              "String",
        "privacy_classification": "Direct Identifier",
        "sensitivity_level":      "High",
        "description":            "Uniquely identifies a student",
        "is_identifier":          True,
        "is_quasi_identifier":    False,
        "is_sensitive":           False,
    },
    "Age": {
        "display_name":           "Age",
        "data_type":              "Integer",
        "privacy_classification": "Quasi-Identifier",
        "sensitivity_level":      "Medium",
        "description":            "Can contribute to re-identification",
        "is_identifier":          False,
        "is_quasi_identifier":    True,
        "is_sensitive":           False,
    },
    "Gender": {
        "display_name":           "Gender",
        "data_type":              "Categorical",
        "privacy_classification": "Quasi-Identifier",
        "sensitivity_level":      "Medium",
        "description":            "Can contribute to uniqueness when combined with other attributes",
        "is_identifier":          False,
        "is_quasi_identifier":    True,
        "is_sensitive":           False,
    },
    "PIN_Code": {
        "display_name":           "PIN Code",
        "data_type":              "String",
        "privacy_classification": "Quasi-Identifier",
        "sensitivity_level":      "High",
        "description":            "Geographic information; can contribute to re-identification",
        "is_identifier":          False,
        "is_quasi_identifier":    True,
        "is_sensitive":           False,
    },
    "Department": {
        "display_name":           "Department",
        "data_type":              "Categorical",
        "privacy_classification": "Quasi-Identifier",
        "sensitivity_level":      "Medium",
        "description":            "Academic grouping that can contribute to record uniqueness",
        "is_identifier":          False,
        "is_quasi_identifier":    True,
        "is_sensitive":           False,
    },
    "CGPA": {
        "display_name":           "CGPA",
        "data_type":              "Float",
        "privacy_classification": "Sensitive Attribute",
        "sensitivity_level":      "High",
        "description":            "Academic performance information",
        "is_identifier":          False,
        "is_quasi_identifier":    False,
        "is_sensitive":           True,
    },
    "Scholarship": {
        "display_name":           "Scholarship",
        "data_type":              "Categorical",
        "privacy_classification": "Sensitive Attribute",
        "sensitivity_level":      "High",
        "description":            "Financial/benefit-related information",
        "is_identifier":          False,
        "is_quasi_identifier":    False,
        "is_sensitive":           True,
    },
}

# Derived attribute-role lists (driven by metadata, not hard-coded)
QI_ATTRIBUTES        = [c for c, m in ATTRIBUTE_METADATA.items() if m["is_quasi_identifier"]]
DIRECT_IDENTIFIERS   = [c for c, m in ATTRIBUTE_METADATA.items() if m["is_identifier"]]
SENSITIVE_ATTRIBUTES = [c for c, m in ATTRIBUTE_METADATA.items() if m["is_sensitive"]]


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_dataset(df):
    """Return a list of human-readable warning strings for dataset issues."""
    warnings = []

    # Unique IDs
    dup_ids = df["Student_ID"].duplicated().sum()
    if dup_ids:
        warnings.append(f"  {dup_ids} duplicate Student ID(s) detected.")

    # Age range (typical student range)
    bad_age = ((df["Age"] < 17) | (df["Age"] > 35)).sum()
    if bad_age:
        warnings.append(f"  {bad_age} record(s) with Age outside 17-35.")

    # CGPA range 0-10
    bad_cgpa = ((df["CGPA"] < 0) | (df["CGPA"] > 10)).sum()
    if bad_cgpa:
        warnings.append(f"  {bad_cgpa} record(s) with CGPA outside 0-10.")

    # Gender values
    bad_gender = (~df["Gender"].str.lower().isin({"male", "female"})).sum()
    if bad_gender:
        warnings.append(f"  {bad_gender} record(s) with unexpected Gender value.")

    # Scholarship values
    bad_schol = (~df["Scholarship"].str.lower().isin({"yes", "no"})).sum()
    if bad_schol:
        warnings.append(f"  {bad_schol} record(s) with unexpected Scholarship value.")

    # Missing values
    for col in df.columns:
        n = df[col].isnull().sum()
        if n:
            display = DISPLAY_NAME_MAP.get(col, col)
            warnings.append(f"  {n} missing value(s) in '{display}'.")

    return warnings


# ============================================================
# MAIN APPLICATION CLASS
# ============================================================

class PrivacyMaskingApp:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "Privacy-Preserving Data Masking System - Student Dataset DP A1"
        )
        self.root.geometry("1500x870")
        self.root.minsize(1100, 720)
        self.root.configure(bg="#F3F4F6")

        # --- State ---
        self.df          = None   # Original df; NEVER modified
        self.result_df   = None   # Current masking result
        self.all_results = {}     # All results keyed by technique name

        # --- Build UI ---
        self.create_styles()
        self.create_header()
        self.create_controls()
        self.create_tabs()
        self.create_status_bar()

    # ==============================================================
    # STYLES
    # ==============================================================

    def create_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Segoe UI", 9),
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#1F2937",
            foreground="white",
        )
        style.map("Treeview.Heading", background=[("active", "#374151")])
        style.configure("TButton",        font=("Segoe UI", 10, "bold"), padding=7)
        style.configure("TLabel",         font=("Segoe UI", 10))
        style.configure("TNotebook.Tab",  font=("Segoe UI", 9, "bold"), padding=(10, 5))

    # ==============================================================
    # HEADER
    # ==============================================================

    def create_header(self):
        header = tk.Frame(self.root, bg="#1F2937", height=95)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Privacy-Preserving Data Masking System",
            bg="#1F2937", fg="white",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(14, 2))
        tk.Label(
            header,
            text=(
                "Re-identification Risk Analysis and Privacy-Preserving Data Release  |  "
                "Student Dataset DP A1  |  25 Records x 7 Attributes"
            ),
            bg="#1F2937", fg="#D1D5DB",
            font=("Segoe UI", 10),
        ).pack()

    # ==============================================================
    # CONTROLS
    # ==============================================================

    def create_controls(self):
        container = tk.Frame(self.root, bg="#E8ECF1")
        container.pack(fill="x")
        inner = tk.Frame(container, bg="#E8ECF1")
        inner.pack(fill="x", padx=15, pady=8)

        # Row 1 – file loading
        row1 = tk.Frame(inner, bg="#E8ECF1")
        row1.pack(fill="x", pady=3)
        ttk.Button(row1, text="Load Excel Dataset",
                   command=self.load_excel).pack(side="left", padx=5)
        self.file_label = tk.Label(
            row1, text="No file selected",
            bg="#E8ECF1", fg="#4B5563", font=("Segoe UI", 10),
        )
        self.file_label.pack(side="left", padx=10)

        # Row 2 – masking controls
        row2 = tk.Frame(inner, bg="#E8ECF1")
        row2.pack(fill="x", pady=5)
        tk.Label(row2, text="Category:", bg="#E8ECF1",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(5, 3))
        self.category_var = tk.StringVar(value="Non-Perturbative")
        self.category_combo = ttk.Combobox(
            row2, textvariable=self.category_var, state="readonly",
            values=["Non-Perturbative", "Perturbative"], width=20,
        )
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.update_techniques)

        tk.Label(row2, text="Technique:", bg="#E8ECF1",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(20, 3))
        self.technique_var = tk.StringVar(value="Suppression")
        self.technique_combo = ttk.Combobox(
            row2, textvariable=self.technique_var, state="readonly",
            values=["Suppression", "Generalization", "Top/Bottom Coding", "Aggregation"],
            width=22,
        )
        self.technique_combo.pack(side="left", padx=5)
        ttk.Button(row2, text="Apply Masking",
                   command=self.apply_masking).pack(side="left", padx=15)
        ttk.Button(row2, text="Export Current Result",
                   command=self.export_current).pack(side="left", padx=5)
        ttk.Button(row2, text="Export All Results",
                   command=self.export_all_results).pack(side="left", padx=5)

    # ==============================================================
    # TABS
    # ==============================================================

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # Tab 1 – Dataset Overview
        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="Dataset Overview")
        self._build_profile_tab()

        # Tab 2 – Original Dataset
        self.original_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.original_tab, text="Original Dataset")
        self.original_tree = self.create_tree(self.original_tab)

        # Tab 3 – Attribute Classification
        self.classification_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.classification_tab, text="Attribute Classification")
        self.classification_tree = self.create_tree(self.classification_tab)

        # Tab 4 – Privacy Risk Analysis
        self.risk_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.risk_tab, text="Privacy Risk Analysis")
        self._build_risk_tab()

        # Tab 5 – Masked Dataset
        self.masked_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.masked_tab, text="Masked Dataset")
        self.masked_tree = self.create_tree(self.masked_tab)

        # Tab 6 – Before vs After
        self.before_after_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.before_after_tab, text="Before vs After")
        self.before_after_tree = self.create_tree(self.before_after_tab)

        # Tab 7 – Dashboard
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.create_dashboard()

    # ==============================================================
    # DATASET OVERVIEW / PROFILE TAB
    # ==============================================================

    def _build_profile_tab(self):
        self.profile_text = tk.Text(
            self.profile_tab, font=("Consolas", 10),
            bg="#FAFAFA", fg="#1F2937", wrap="none", state="disabled",
        )
        sb_y = ttk.Scrollbar(self.profile_tab, orient="vertical",
                              command=self.profile_text.yview)
        sb_x = ttk.Scrollbar(self.profile_tab, orient="horizontal",
                              command=self.profile_text.xview)
        self.profile_text.configure(yscrollcommand=sb_y.set,
                                    xscrollcommand=sb_x.set)
        sb_y.pack(side="right",  fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.profile_text.pack(fill="both", expand=True)

    def _update_profile(self):
        if self.df is None:
            return
        df = self.df
        sep = "=" * 72

        lines = [
            sep,
            " DATASET PROFILE  -  Student Dataset DP A1",
            sep,
            f"  Total Records       : {len(df)}",
            f"  Total Attributes    : {len(df.columns)}",
            f"  Missing Values      : {df.isnull().sum().sum()}",
            f"  Duplicate Rows      : {df.duplicated().sum()}",
            f"  Numeric Attributes  : {len(df.select_dtypes(include='number').columns)}",
            f"  Categorical Attrs   : {len(df.select_dtypes(exclude='number').columns)}",
            "",
        ]

        hdr = (f"  {'Attribute':<16} {'Type':<12} {'Non-null':<10}"
               f" {'Missing':<9} {'Unique':<8} {'Min':<10} {'Max':<10} {'Mean':<10}")
        lines.append(hdr)
        lines.append("  " + "-" * 88)

        for col in df.columns:
            dtype   = str(df[col].dtype)
            nonnull = df[col].notna().sum()
            missing = df[col].isna().sum()
            unique  = df[col].nunique()
            display = DISPLAY_NAME_MAP.get(col, col)
            if pd.api.types.is_numeric_dtype(df[col]):
                mn   = f"{df[col].min():.2f}"
                mx   = f"{df[col].max():.2f}"
                mean = f"{df[col].mean():.2f}"
            else:
                mn = mx = mean = "-"
            lines.append(
                f"  {display:<16} {dtype:<12} {nonnull:<10}"
                f" {missing:<9} {unique:<8} {mn:<10} {mx:<10} {mean:<10}"
            )

        lines += [
            "",
            sep,
            " ATTRIBUTE PRIVACY CLASSIFICATION",
            sep,
            f"  {'Attribute':<16} {'Classification':<22} {'Sensitivity':<14} Reason",
            "  " + "-" * 88,
        ]
        for col in df.columns:
            meta    = ATTRIBUTE_METADATA.get(col, {})
            cls     = meta.get("privacy_classification", "Unknown")
            sens    = meta.get("sensitivity_level", "-")
            reason  = meta.get("description", "-")
            display = DISPLAY_NAME_MAP.get(col, col)
            lines.append(f"  {display:<16} {cls:<22} {sens:<14} {reason}")

        lines += ["", sep, " CATEGORY DISTRIBUTIONS", sep]
        for col in df.select_dtypes(exclude="number").columns:
            display = DISPLAY_NAME_MAP.get(col, col)
            lines.append(f"\n  {display}:")
            for val, cnt in df[col].value_counts().items():
                pct = cnt / len(df) * 100
                lines.append(f"    {str(val):<22} {cnt:>4}  ({pct:.1f}%)")
        lines.append("")

        self.profile_text.configure(state="normal")
        self.profile_text.delete("1.0", "end")
        self.profile_text.insert("end", "\n".join(lines))
        self.profile_text.configure(state="disabled")

    # ==============================================================
    # PRIVACY RISK ANALYSIS TAB
    # ==============================================================

    def _build_risk_tab(self):
        top = tk.Frame(self.risk_tab, bg="#F3F4F6")
        top.pack(fill="x", padx=5, pady=5)
        self.risk_summary_text = tk.Text(
            top, font=("Consolas", 9),
            bg="#F0F4F8", fg="#1F2937", height=14,
            wrap="none", state="disabled",
        )
        sb_x = ttk.Scrollbar(top, orient="horizontal",
                              command=self.risk_summary_text.xview)
        self.risk_summary_text.configure(xscrollcommand=sb_x.set)
        sb_x.pack(side="bottom", fill="x")
        self.risk_summary_text.pack(fill="x")

        tk.Label(
            self.risk_tab,
            text="Per-Record Re-identification Risk",
            font=("Segoe UI", 10, "bold"),
            bg="#F3F4F6",
        ).pack(anchor="w", padx=8)
        self.risk_tree = self.create_tree(self.risk_tab)

    # ==============================================================
    # TREEVIEW FACTORY
    # ==============================================================

    def create_tree(self, parent):
        """Create a Treeview with both scrollbars inside parent."""
        frame = tk.Frame(parent, bg="#FFFFFF")
        frame.pack(fill="both", expand=True)
        tree     = ttk.Treeview(frame, show="headings", selectmode="browse")
        y_scroll = ttk.Scrollbar(frame, orient="vertical",  command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side="right",  fill="y")
        x_scroll.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        return tree

    # ==============================================================
    # DASHBOARD
    # ==============================================================

    def create_dashboard(self):
        self._dash_cards = {}
        tk.Label(
            self.dashboard_tab, text="Dataset Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="#F3F4F6", fg="#1F2937",
        ).pack(pady=12)

        cards_frame = tk.Frame(self.dashboard_tab, bg="#F3F4F6")
        cards_frame.pack(pady=5, padx=15, fill="x")

        card_defs = [
            ("TOTAL RECORDS",        "records",      "#2563EB"),
            ("TOTAL ATTRIBUTES",     "attributes",   "#7C3AED"),
            ("MISSING VALUES",       "missing",      "#DC2626"),
            ("DUPLICATE ROWS",       "duplicates",   "#D97706"),
            ("UNIQUE DEPARTMENTS",   "departments",  "#059669"),
            ("AVERAGE CGPA",         "avg_cgpa",     "#0891B2"),
            ("QI ATTRIBUTES",        "qi_count",     "#6366F1"),
            ("SENSITIVE ATTRIBUTES", "sensitive",    "#BE185D"),
            ("DIRECT IDENTIFIERS",   "identifiers",  "#92400E"),
            ("CURRENT RISK LEVEL",   "risk_level",   "#1F2937"),
        ]

        cols = 5
        for idx, (label, key, color) in enumerate(card_defs):
            row_n = idx // cols
            col_n = idx % cols
            card  = tk.Frame(cards_frame, bg=color, width=200, height=100)
            card.grid(row=row_n, column=col_n, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)
            cards_frame.columnconfigure(col_n, weight=1)
            tk.Label(
                card, text=label,
                bg=color, fg="white",
                font=("Segoe UI", 8, "bold"),
                wraplength=170,
            ).pack(pady=(14, 2))
            val_lbl = tk.Label(
                card, text="-",
                bg=color, fg="white",
                font=("Segoe UI", 20, "bold"),
            )
            val_lbl.pack()
            self._dash_cards[key] = val_lbl

        self.activity_label = tk.Label(
            self.dashboard_tab,
            text="No masking applied yet.",
            font=("Segoe UI", 10),
            bg="#F3F4F6", fg="#4B5563",
        )
        self.activity_label.pack(pady=10)

    def update_dashboard(self, technique=None):
        if self.df is None:
            return
        df = self.df
        try:
            qi     = [c for c in QI_ATTRIBUTES if c in df.columns]
            groups = df.groupby(qi)["Student_ID"].transform("count")
            avg_r  = (1.0 / groups).mean()
            risk_lbl = ("HIGH" if avg_r >= 0.5
                        else "MEDIUM" if avg_r >= 0.2
                        else "LOW")
        except Exception:
            risk_lbl = "-"

        updates = {
            "records":     str(len(df)),
            "attributes":  str(len(df.columns)),
            "missing":     str(df.isnull().sum().sum()),
            "duplicates":  str(df.duplicated().sum()),
            "departments": str(df["Department"].nunique()),
            "avg_cgpa":    f"{df['CGPA'].mean():.2f}",
            "qi_count":    str(len([c for c in QI_ATTRIBUTES        if c in df.columns])),
            "sensitive":   str(len([c for c in SENSITIVE_ATTRIBUTES  if c in df.columns])),
            "identifiers": str(len([c for c in DIRECT_IDENTIFIERS    if c in df.columns])),
            "risk_level":  risk_lbl,
        }
        for key, val in updates.items():
            if key in self._dash_cards:
                self._dash_cards[key].config(text=val)

        if technique and self.result_df is not None:
            self.activity_label.config(
                text=(f"Last masking: {technique}  |  "
                      f"{len(self.result_df)} records, "
                      f"{len(self.result_df.columns)} attributes")
            )

    # ==============================================================
    # STATUS BAR
    # ==============================================================

    def create_status_bar(self):
        self.status = tk.Label(
            self.root,
            text="Ready  -  Load an Excel dataset to begin.",
            bg="#E5E7EB", fg="#374151",
            anchor="w", padx=10,
            font=("Segoe UI", 9),
        )
        self.status.pack(fill="x", side="bottom")

    # ==============================================================
    # LOAD EXCEL
    # ==============================================================

    def load_excel(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Excel Dataset",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files",   "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            # Try named sheet first; fall back to first sheet
            try:
                raw = pd.read_excel(file_path, sheet_name="Student_Data", dtype=str)
            except Exception:
                raw = pd.read_excel(file_path, dtype=str)

            # Strip whitespace from column names
            raw.columns = raw.columns.str.strip()

            # Rename columns from Excel format to internal format
            rename_map = {ec: ic for ec, ic in COLUMN_RENAME_MAP.items()
                          if ec in raw.columns}
            raw.rename(columns=rename_map, inplace=True)

            # Check that all required columns are present
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
            if missing_cols:
                messagebox.showerror(
                    "Invalid Dataset",
                    "Missing required columns:\n\n"
                    + "\n".join(DISPLAY_NAME_MAP.get(c, c) for c in missing_cols),
                )
                return

            # Type coercion
            raw["Age"]      = pd.to_numeric(raw["Age"],  errors="coerce")
            raw["CGPA"]     = pd.to_numeric(raw["CGPA"], errors="coerce")
            raw["PIN_Code"] = raw["PIN_Code"].astype(str).str.strip()

            # Normalize categorical columns
            raw["Gender"]     = raw["Gender"].str.strip().str.title()
            raw["Scholarship"] = raw["Scholarship"].str.strip().str.title()
            for col in raw.select_dtypes(include="object").columns:
                raw[col] = raw[col].str.strip()

            # Validate
            warns = validate_dataset(raw)

            self.df          = raw
            self.result_df   = None
            self.all_results = {}

            fname = file_path.replace("\\", "/").split("/")[-1]
            self.file_label.config(text=fname)

            # Populate all tabs
            self.display_dataframe(self.df, self.original_tree, use_display_names=True)
            self._update_profile()
            self.show_classification()
            self.show_risk()
            self.update_dashboard()
            self.notebook.select(self.original_tab)

            self.status.config(
                text=f"Loaded {len(self.df)} records and {len(self.df.columns)} attributes."
            )

            if warns:
                messagebox.showwarning(
                    "Dataset Warnings",
                    "Dataset loaded with the following warnings:\n\n" + "\n".join(warns),
                )
            else:
                messagebox.showinfo(
                    "Dataset Loaded",
                    (f"Successfully loaded {len(self.df)} records "
                     f"and {len(self.df.columns)} attributes.\n"
                     "No validation issues detected."),
                )

        except Exception as error:
            messagebox.showerror(
                "Load Error",
                f"Unable to load dataset:\n\n{error}",
            )

    # ==============================================================
    # DISPLAY DATAFRAME IN TREEVIEW
    # ==============================================================

    def display_dataframe(self, data, tree, use_display_names=False):
        """Clear and repopulate a Treeview with DataFrame contents."""
        for item in tree.get_children():
            tree.delete(item)
        tree["columns"] = []

        if data is None or data.empty:
            return

        columns = list(data.columns)
        tree["columns"] = columns

        for col in columns:
            heading = DISPLAY_NAME_MAP.get(col, col) if use_display_names else col
            tree.heading(col, text=heading)
            tree.column(col, width=150, minwidth=80, anchor="center")

        for _, row in data.iterrows():
            tree.insert(
                "", "end",
                values=["" if pd.isna(v) else str(v) for v in row],
            )

    # ==============================================================
    # TECHNIQUE SWITCHER
    # ==============================================================

    def update_techniques(self, event=None):
        if self.category_var.get() == "Non-Perturbative":
            techs = ["Suppression", "Generalization", "Top/Bottom Coding", "Aggregation"]
        else:
            techs = ["Noise Addition", "Data Swapping",
                     "Differential Privacy", "Synthetic Data"]
        self.technique_combo["values"] = techs
        self.technique_var.set(techs[0])

    # ==============================================================
    # APPLY MASKING (dispatcher)
    # ==============================================================

    def apply_masking(self):
        if self.df is None:
            messagebox.showwarning("No Dataset", "Load an Excel dataset first.")
            return

        technique = self.technique_var.get()
        dispatch = {
            "Suppression":          self.suppression,
            "Generalization":       self.generalization,
            "Top/Bottom Coding":    self.top_bottom_coding,
            "Aggregation":          self.aggregation,
            "Noise Addition":       self.noise_addition,
            "Data Swapping":        self.data_swapping,
            "Differential Privacy": self.differential_privacy,
            "Synthetic Data":       self.synthetic_data,
        }
        fn = dispatch.get(technique)
        if fn is None:
            return

        try:
            result = fn(self.df)
        except Exception as error:
            messagebox.showerror("Masking Error", str(error))
            return

        self.result_df = result
        self.all_results[technique] = result

        self.display_dataframe(result, self.masked_tree)
        self._update_before_after(technique)
        self.update_dashboard(technique=technique)
        self.notebook.select(self.masked_tab)
        self.status.config(
            text=(f"{technique} completed: "
                  f"{len(result)} records, "
                  f"{len(result.columns)} attributes released.")
        )

    # ==============================================================
    # BEFORE vs AFTER COMPARISON
    # ==============================================================

    def _update_before_after(self, technique):
        if self.df is None or self.result_df is None:
            return
        orig   = self.df
        masked = self.result_df
        rows   = []

        def add(metric, before, after, change=""):
            rows.append({
                "Metric": metric,
                "Before": str(before),
                "After":  str(after),
                "Change": change,
            })

        # Counts
        add("Records",    len(orig), len(masked))
        add("Attributes", len(orig.columns), len(masked.columns),
            (f"{len(orig.columns) - len(masked.columns)} removed"
             if len(orig.columns) != len(masked.columns)
             else "unchanged"))

        # Student IDs
        if "Student_ID" in orig.columns:
            add(
                "Unique Student IDs",
                orig["Student_ID"].nunique(),
                "Suppressed" if "Student_ID" not in masked.columns
                else masked["Student_ID"].nunique(),
            )

        # CGPA utility
        if "CGPA" in orig.columns and "CGPA" in masked.columns:
            bm = round(orig["CGPA"].mean(),   4)
            am = round(masked["CGPA"].mean(), 4)
            d  = round(abs(bm - am), 4)
            u  = round((1 - d / bm) * 100, 1) if bm else 0
            add("Mean CGPA", bm, am, f"Delta {d}")
            add("CGPA Std Dev",
                round(orig["CGPA"].std(),   4),
                round(masked["CGPA"].std(), 4))
            add("CGPA Utility Retention", "100%", f"{u}%")

        # Re-identification risk
        def avg_risk(df):
            qi = [c for c in QI_ATTRIBUTES if c in df.columns]
            if not qi:
                return None
            try:
                id_col = "Student_ID" if "Student_ID" in df.columns else df.columns[0]
                grp    = df.groupby(qi)[id_col].transform("count")
                return round((1.0 / grp).mean(), 4)
            except Exception:
                return None

        or_ = avg_risk(orig)
        mr_ = avg_risk(masked)
        if or_ is not None:
            add("Avg Re-identification Risk", or_,
                mr_ if mr_ is not None else "N/A",
                "Reduced" if mr_ and mr_ < or_ else "-")
            if or_ and mr_:
                add("Privacy Risk Reduction",
                    "0%", f"{round((1 - mr_ / or_) * 100, 1)}%")

        # QI groups
        def qi_groups(df):
            qi = [c for c in QI_ATTRIBUTES if c in df.columns]
            if not qi:
                return None
            try:
                return df.groupby(qi).ngroups
            except Exception:
                return None

        og = qi_groups(orig)
        mg = qi_groups(masked)
        if og is not None:
            add("Unique QI Groups", og, mg if mg is not None else "N/A")

        # Scholarship distribution
        if "Scholarship" in orig.columns and "Scholarship" in masked.columns:
            by = (orig["Scholarship"].str.lower()   == "yes").sum()
            ay = (masked["Scholarship"].str.lower() == "yes").sum()
            add("Scholarship = Yes (count)", by, ay)

        comp = pd.DataFrame(rows, columns=["Metric", "Before", "After", "Change"])
        self.display_dataframe(comp, self.before_after_tree)
        self.all_results[f"BeforeAfter_{technique}"] = comp

    # ==============================================================
    # 1. SUPPRESSION
    # ==============================================================

    def suppression(self, data):
        """
        Suppress the direct identifier (Student_ID).
        Partially mask PIN_Code (retain first 3 digits + ***).
        Released: Age, Gender, PIN_Code(masked), Department, CGPA, Scholarship.
        """
        result = data.copy()
        result["PIN_Code"] = (
            result["PIN_Code"].astype(str).str[:3] + "***"
        )
        released = ["Age", "Gender", "PIN_Code", "Department", "CGPA", "Scholarship"]
        return result[[c for c in released if c in result.columns]]

    # ==============================================================
    # 2. GENERALIZATION
    # ==============================================================

    def generalization(self, data):
        """
        Age     : Age bands derived dynamically from actual dataset range.
        PIN_Code: Geographic region (first 3 digits + ***).
        Released: Age(generalized), Gender, PIN_Code(region), Department, CGPA, Scholarship.
        """
        result  = data.copy()
        age_min = int(data["Age"].min())
        age_max = int(data["Age"].max())
        cut1    = age_min + (age_max - age_min) // 3
        cut2    = age_min + 2 * (age_max - age_min) // 3

        def age_group(age):
            if pd.isna(age):
                return "Unknown"
            if age <= cut1:
                return f"<={cut1}"
            if age <= cut2:
                return f"{cut1 + 1}-{cut2}"
            return f"{cut2 + 1}+"

        result["Age"]      = result["Age"].apply(age_group)
        result["PIN_Code"] = result["PIN_Code"].astype(str).str[:3] + "***"
        released = ["Age", "Gender", "PIN_Code", "Department", "CGPA", "Scholarship"]
        return result[[c for c in released if c in result.columns]]

    # ==============================================================
    # 3. TOP / BOTTOM CODING
    # ==============================================================

    def top_bottom_coding(self, data):
        """
        Age  : Bottom-coded at dataset 5th-pct; top-coded at 95th-pct.
        CGPA : Clipped to dataset 5th–95th percentile range.
        Released: Age(coded), Gender, Department, CGPA(clipped), Scholarship.
        """
        result    = data.copy()
        age_low   = float(data["Age"].quantile(0.05))
        age_high  = float(data["Age"].quantile(0.95))
        cgpa_low  = round(float(data["CGPA"].quantile(0.05)), 2)
        cgpa_high = round(float(data["CGPA"].quantile(0.95)), 2)

        def code_age(age):
            if pd.isna(age):
                return "Unknown"
            if age <= age_low:
                return f"<={int(age_low)}"
            if age >= age_high:
                return f">={int(age_high)}"
            return age

        result["Age"]  = result["Age"].apply(code_age)
        result["CGPA"] = result["CGPA"].clip(lower=cgpa_low, upper=cgpa_high).round(2)
        released = ["Age", "Gender", "Department", "CGPA", "Scholarship"]
        return result[[c for c in released if c in result.columns]]

    # ==============================================================
    # 4. AGGREGATION
    # ==============================================================

    def aggregation(self, data):
        """
        Group by Department; compute count, avg/min/max CGPA, Scholarship rate.
        Individual-level records are NOT released.
        """
        result = (
            data.groupby("Department", as_index=False)
            .agg(
                Number_of_Students=("Student_ID", "count"),
                Average_CGPA=("CGPA", "mean"),
                Maximum_CGPA=("CGPA", "max"),
                Minimum_CGPA=("CGPA", "min"),
            )
        )
        result["Average_CGPA"] = result["Average_CGPA"].round(2)

        def schol_rate(dept):
            dept_df = data[data["Department"] == dept]
            yes     = (dept_df["Scholarship"].str.lower() == "yes").sum()
            total   = len(dept_df)
            if not total:
                return "0"
            return f"{yes}/{total} ({round(yes / total * 100, 1)}%)"

        result["Scholarship_Rate"] = result["Department"].apply(schol_rate)
        return result

    # ==============================================================
    # 5. NOISE ADDITION
    # ==============================================================

    def noise_addition(self, data):
        """
        Add Gaussian noise N(0, 0.05) to CGPA values.
        Noise seed: 42 (reproducible).
        CGPA clipped to [0, 10] after perturbation.
        Utility metrics shown in status bar.
        """
        rng       = np.random.default_rng(42)
        orig_cgpa = data["CGPA"].to_numpy(dtype=float)
        noise     = np.round(rng.normal(0, 0.05, len(data)), 2)
        noisy     = np.clip(orig_cgpa + noise, 0, 10).round(2)

        result = pd.DataFrame({
            "Age":        data["Age"].values,
            "Gender":     data["Gender"].values,
            "Department": data["Department"].values,
            "Scholarship": data["Scholarship"].values,
            "CGPA":       noisy,
        })

        om = round(float(np.nanmean(orig_cgpa)), 4)
        nm = round(float(np.nanmean(noisy)),     4)
        d  = round(abs(om - nm), 4)
        u  = round((1 - d / om) * 100, 2) if om else 0
        self.status.config(
            text=(f"Noise Addition  |  Orig mean CGPA={om}  |  "
                  f"Masked mean={nm}  |  Delta={d}  |  Utility={u}%")
        )
        return result

    # ==============================================================
    # 6. DATA SWAPPING
    # ==============================================================

    def data_swapping(self, data):
        """
        Randomly swap CGPA values between pairs of records.
        Student_ID is NOT swapped; record count and dtypes are preserved.
        """
        rng  = np.random.default_rng(42)
        cgpa = data["CGPA"].to_numpy(dtype=float).copy()
        idxs = list(range(len(cgpa)))
        rng.shuffle(idxs)
        for i in range(0, len(idxs) - 1, 2):
            a, b = idxs[i], idxs[i + 1]
            cgpa[a], cgpa[b] = cgpa[b], cgpa[a]

        return pd.DataFrame({
            "Age":        data["Age"].values,
            "Gender":     data["Gender"].values,
            "Department": data["Department"].values,
            "Scholarship": data["Scholarship"].values,
            "CGPA":       cgpa,
        })

    # ==============================================================
    # 7. DIFFERENTIAL PRIVACY
    # ==============================================================

    def differential_privacy(self, data):
        """
        Apply the Laplace mechanism to COUNT(Scholarship = 'Yes').
        Query sensitivity = 1 (one record changes count by at most 1).
        Epsilon = 1.0 (configurable; smaller => more noise => stronger privacy).
        Noise ~ Laplace(0, sensitivity / epsilon).
        """
        rng         = np.random.default_rng(42)
        epsilon     = 1.0
        sensitivity = 1
        true_count  = int((data["Scholarship"].str.lower() == "yes").sum())
        scale       = sensitivity / epsilon
        noise       = rng.laplace(0, scale)
        private_res = max(0, min(len(data), int(round(true_count + noise))))

        return pd.DataFrame({
            "Query":          ["Number of Scholarship Recipients"],
            "True_Result":    [true_count],
            "Epsilon":        [epsilon],
            "Sensitivity":    [sensitivity],
            "Laplace_Noise":  [round(noise, 4)],
            "Private_Result": [private_res],
            "Note": [
                "Smaller epsilon = stronger privacy (more noise). "
                "Noise ~ Lap(0, sensitivity/epsilon)."
            ],
        })

    # ==============================================================
    # 8. SYNTHETIC DATA
    # ==============================================================

    def synthetic_data(self, data):
        """
        Generate n synthetic records preserving approximate distributions.
        New Synthetic_IDs are assigned (SY001, SY002, ...).
        Original Student_IDs are NOT included.
        CGPA sampled from N(original_mean, original_std), clipped to actual range.
        """
        rng = np.random.default_rng(42)
        n   = len(data)

        gp = data["Gender"].value_counts(normalize=True)
        dp = data["Department"].value_counts(normalize=True)
        sp = data["Scholarship"].value_counts(normalize=True)

        cgpa_mean = float(data["CGPA"].mean())
        cgpa_std  = float(data["CGPA"].std())
        cgpa_min  = float(data["CGPA"].min())
        cgpa_max  = float(data["CGPA"].max())

        syn_cgpa = np.round(
            np.clip(rng.normal(cgpa_mean, cgpa_std, n), cgpa_min, cgpa_max), 2
        )

        return pd.DataFrame({
            "Synthetic_ID": [f"SY{i:03d}" for i in range(1, n + 1)],
            "Age":          rng.choice(data["Age"].dropna().to_numpy(), n, replace=True),
            "Gender":       rng.choice(gp.index.tolist(), n, replace=True, p=gp.values),
            "Department":   rng.choice(dp.index.tolist(), n, replace=True, p=dp.values),
            "CGPA":         syn_cgpa,
            "Scholarship":  rng.choice(sp.index.tolist(), n, replace=True, p=sp.values),
        })

    # ==============================================================
    # RISK ANALYSIS
    # ==============================================================

    def show_risk(self):
        """
        Calculate per-record QI group size and re-identification risk.
        QI attributes are derived from ATTRIBUTE_METADATA (not hard-coded).
        Also computes a dataset-level risk summary.
        """
        if self.df is None:
            return
        try:
            qi   = [c for c in QI_ATTRIBUTES if c in self.df.columns]
            risk = self.df.copy()

            risk["QI_Group_Size"] = (
                risk.groupby(qi)["Student_ID"].transform("count")
            )
            risk["Reidentification_Risk"] = (
                1.0 / risk["QI_Group_Size"]
            ).round(4)

            def rlevel(r):
                if r >= 0.5:  return "High"
                if r >= 0.2:  return "Medium"
                return "Low"

            risk["Risk_Level"] = risk["Reidentification_Risk"].apply(rlevel)

            dcols = (
                ["Student_ID"] + qi +
                ["QI_Group_Size", "Reidentification_Risk", "Risk_Level"]
            )
            dcols   = [c for c in dcols if c in risk.columns]
            display = risk[dcols].copy()
            display.rename(columns=DISPLAY_NAME_MAP, inplace=True)
            self.display_dataframe(display, self.risk_tree)

            # Dataset-level summary
            total   = len(risk)
            uq      = risk.groupby(qi).ngroups
            uqr     = (risk["QI_Group_Size"] == 1).sum()
            mx      = int(risk["QI_Group_Size"].max())
            mn      = int(risk["QI_Group_Size"].min())
            avg     = round(risk["QI_Group_Size"].mean(), 2)
            hi      = (risk["Risk_Level"] == "High").sum()
            med     = (risk["Risk_Level"] == "Medium").sum()
            lo      = (risk["Risk_Level"] == "Low").sum()
            ar      = round(risk["Reidentification_Risk"].mean(), 4)
            overall = (
                "HIGH"   if ar >= 0.5 or hi > total * 0.3
                else "MEDIUM" if ar >= 0.2 or hi > 0
                else "LOW"
            )

            qi_disp = ", ".join(DISPLAY_NAME_MAP.get(q, q) for q in qi)
            sep = "=" * 62
            lines = [
                sep,
                "  DATASET-LEVEL RE-IDENTIFICATION RISK SUMMARY",
                sep,
                f"  QI Attributes Used        : {qi_disp}",
                f"  Risk Formula              : Risk = 1 / QI_Group_Size",
                "",
                f"  Total Records             : {total}",
                f"  Unique QI Groups          : {uq}",
                f"  Records in Unique Groups  : {uqr}  (group size = 1)",
                f"  Maximum QI Group Size     : {mx}",
                f"  Minimum QI Group Size     : {mn}",
                f"  Average QI Group Size     : {avg}",
                "",
                f"  High-Risk Records         : {hi}   (Risk >= 0.5)",
                f"  Medium-Risk Records       : {med}  (0.2 <= Risk < 0.5)",
                f"  Low-Risk Records          : {lo}   (Risk < 0.2)",
                f"  Avg Re-identification Risk: {ar}",
                "",
                f"  Overall Risk Level        : *** {overall} ***",
                sep,
            ]

            self.risk_summary_text.configure(state="normal")
            self.risk_summary_text.delete("1.0", "end")
            self.risk_summary_text.insert("end", "\n".join(lines))
            self.risk_summary_text.configure(state="disabled")

            self.all_results["Risk_Analysis"] = display

        except Exception as error:
            print("Risk analysis error:", error)

    # ==============================================================
    # ATTRIBUTE CLASSIFICATION
    # ==============================================================

    def show_classification(self):
        """Populate the Attribute Classification tab from ATTRIBUTE_METADATA."""
        if self.df is None:
            return
        rows = []
        for col in self.df.columns:
            meta = ATTRIBUTE_METADATA.get(col, {})
            rows.append({
                "Attribute":      DISPLAY_NAME_MAP.get(col, col),
                "Data_Type":      meta.get("data_type", str(self.df[col].dtype)),
                "Classification": meta.get("privacy_classification", "Unclassified"),
                "Sensitivity":    meta.get("sensitivity_level", "-"),
                "Reason":         meta.get("description", ""),
            })
        cls_df = pd.DataFrame(rows)
        self.display_dataframe(cls_df, self.classification_tree)
        self.all_results["Attribute_Classification"] = cls_df

    # ==============================================================
    # EXPORT — CURRENT RESULT
    # ==============================================================

    def export_current(self):
        if self.result_df is None:
            messagebox.showwarning("No Result", "Apply a masking technique first.")
            return
        tech = (
            self.technique_var.get()
            .replace(" ", "_")
            .replace("/", "_")
        )
        fp = filedialog.asksaveasfilename(
            title="Export Masked Dataset",
            defaultextension=".xlsx",
            initialfile=f"{tech}_masked.xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
        )
        if not fp:
            return
        try:
            with pd.ExcelWriter(fp, engine="openpyxl") as writer:
                self.result_df.to_excel(writer, index=False, sheet_name="Masked_Data")
            messagebox.showinfo("Export Successful",
                                f"Masked dataset exported to:\n{fp}")
            self.status.config(text=f"Exported: {fp}")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))

    # ==============================================================
    # EXPORT — ALL RESULTS
    # ==============================================================

    def export_all_results(self):
        if not self.all_results:
            messagebox.showwarning(
                "No Results",
                "Load the dataset and apply at least one operation.",
            )
            return
        fp = filedialog.asksaveasfilename(
            title="Export All Results",
            defaultextension=".xlsx",
            initialfile="privacy_masking_all_results.xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
        )
        if not fp:
            return
        try:
            with pd.ExcelWriter(fp, engine="openpyxl") as writer:
                # Original data always first
                if self.df is not None:
                    od = self.df.copy()
                    od.rename(columns=DISPLAY_NAME_MAP, inplace=True)
                    od.to_excel(writer, index=False, sheet_name="Original_Data")

                for sname, df in self.all_results.items():
                    safe = sname.replace("/", "_").replace("\\", "_")[:31]
                    df.to_excel(writer, index=False, sheet_name=safe)

            messagebox.showinfo(
                "Export Successful",
                (f"All results exported to:\n{fp}\n\n"
                 f"Sheets: Original_Data + {len(self.all_results)} result sheet(s).")
            )
            self.status.config(text=f"All results exported: {fp}")
        except Exception as error:
            messagebox.showerror("Export Error", str(error))


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = PrivacyMaskingApp(root)
    root.mainloop()
