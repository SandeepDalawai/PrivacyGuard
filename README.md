# Privacy-Preserving Data Masking System
### Student Dataset DP A1 — Execution Guide

---

## Quick Start

Open **PowerShell** or **Command Prompt** and run:

```powershell
cd "c:\Users\dalaw\Downloads\DP A1 Software"
python -m pip install pandas numpy openpyxl
python app.py
```

That's it. The application window will open.

---

## Step-by-Step Instructions

### Step 1 — Install Python (if not installed)
Download Python 3.10 or later from: https://www.python.org/downloads/

During installation, check **"Add Python to PATH"**.

---

### Step 2 — Install Required Libraries

Open PowerShell and run:

```powershell
python -m pip install pandas numpy openpyxl
```

---

### Step 3 — Run the Application

```powershell
cd "c:\Users\dalaw\Downloads\DP A1 Software"
python app.py
```

The window titled **"Privacy-Preserving Data Masking System"** will appear.

---

### Step 4 — Load the Dataset

1. Click the **"Load Excel Dataset"** button (top-left)
2. Browse to: `c:\Users\dalaw\Downloads\DP A1 Software\`
3. Select: **Student Dataset DP A1.xlsx**
4. Click **Open**

The application will load **25 records × 7 attributes** and show a confirmation.

---

### Step 5 — Explore the Tabs

| Tab | What It Shows |
|-----|---------------|
| **Dataset Overview** | Full data profile — column stats, privacy classification, category distributions |
| **Original Dataset** | All 25 original student records |
| **Attribute Classification** | Privacy classification table (Direct Identifier / Quasi-Identifier / Sensitive) |
| **Privacy Risk Analysis** | Dataset-level risk summary + per-record re-identification risk |
| **Masked Dataset** | Output after applying a masking technique |
| **Before vs After** | Comparison metrics: utility, risk reduction, CGPA difference |
| **Dashboard** | 10 live metric cards: records, attributes, departments, avg CGPA, risk level, etc. |

---

### Step 6 — Apply Masking

1. Choose a **Category** from the dropdown:
   - `Non-Perturbative` → Suppression, Generalization, Top/Bottom Coding, Aggregation
   - `Perturbative`     → Noise Addition, Data Swapping, Differential Privacy, Synthetic Data

2. Choose a **Technique** from the second dropdown

3. Click **"Apply Masking"**

4. The **Masked Dataset** tab opens automatically with the result

5. Check the **Before vs After** tab for utility and privacy metrics

---

### Step 7 — Export Results

| Button | Action |
|--------|--------|
| **Export Current Result** | Saves the current masked dataset as `.xlsx` |
| **Export All Results** | Saves a multi-sheet Excel file with Original Data + all masking results + risk analysis + attribute classification |

---

## Masking Techniques Reference

### Non-Perturbative
| Technique | What It Does |
|-----------|-------------|
| **Suppression** | Removes Student ID; masks PIN Code as `560***` |
| **Generalization** | Groups Age into bands (`<=21`, `22-22`, `23+`); regions PIN Code |
| **Top/Bottom Coding** | Clips Age and CGPA at dataset 5th–95th percentile boundaries |
| **Aggregation** | Groups by Department; releases count, avg/min/max CGPA, scholarship rate |

### Perturbative
| Technique | What It Does |
|-----------|-------------|
| **Noise Addition** | Adds Gaussian noise N(0, 0.05) to CGPA; clips to valid range [0, 10] |
| **Data Swapping** | Randomly swaps CGPA values between record pairs |
| **Differential Privacy** | Applies Laplace mechanism to Scholarship count query (ε=1.0) |
| **Synthetic Data** | Generates 25 new synthetic records preserving distributions; assigns SY001–SY025 IDs |

---

## Files in This Folder

```
DP A1 Software/
├── app.py                        ← Main application (run this)
└── Student Dataset DP A1.xlsx   ← Input dataset (25 records, 7 attributes)
```

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| Python | 3.10 or later |
| pandas | Any recent version |
| numpy | Any recent version |
| openpyxl | Any recent version |
| OS | Windows 10/11 (Tkinter included with Python) |
| Screen | 1100 × 720 minimum; 1500 × 870 recommended |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not recognized | Add Python to PATH or use full path: `C:\Python3xx\python.exe app.py` |
| `ModuleNotFoundError: pandas` | Run `python -m pip install pandas numpy openpyxl` |
| Window does not appear | Ensure you are running on a machine with a display (not a headless server) |
| Dataset fails to load | Ensure you select `Student Dataset DP A1.xlsx` from the correct folder |
| Export fails | Choose a save location where you have write permission (e.g., Desktop or Documents) |

---

## Privacy Attributes Quick Reference

| Attribute | Classification | Sensitivity |
|-----------|---------------|-------------|
| Student ID | Direct Identifier | High |
| Age | Quasi-Identifier | Medium |
| Gender | Quasi-Identifier | Medium |
| PIN Code | Quasi-Identifier | High |
| Department | Quasi-Identifier | Medium |
| CGPA | Sensitive Attribute | High |
| Scholarship | Sensitive Attribute | High |
