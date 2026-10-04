# PrivacyGuard — Privacy-Preserving Microdata Anonymization

> A privacy engineering project for analysing re-identification risk in microdata, applying data masking techniques, and evaluating privacy–utility trade-offs.

## Overview

**PrivacyGuard** is a Data Privacy and Privacy Engineering project focused on the secure release of microdata.

Removing direct identifiers such as Student ID does not necessarily make a dataset anonymous. An attacker may combine **quasi-identifiers** such as age, gender, PIN code, and department with external knowledge to identify an individual and infer sensitive information.

This project demonstrates a structured approach to reducing such risks through **re-identification analysis, non-perturbative masking, perturbative masking, and privacy–utility evaluation**.

The project uses a fictional student dataset containing 25 records and demonstrates how different masking strategies affect privacy protection and analytical utility.

---

## Problem Statement

Microdata provides valuable record-level information for research and analysis, but releasing detailed records can introduce privacy risks.

Even when direct identifiers are removed, combinations of seemingly harmless attributes can uniquely distinguish individuals.

For example:

```text
Age + Gender + PIN Code + Department
```

may form a unique combination within a dataset.

The objective is therefore not simply to remove identifiers, but to **reduce re-identification risk while preserving as much useful information as possible**.

---

## Objectives

* Identify direct identifiers, quasi-identifiers, and sensitive attributes.
* Measure re-identification risk using equivalence-class analysis.
* Apply privacy-preserving data-masking techniques.
* Evaluate privacy improvement and information loss.
* Analyse the privacy–utility trade-off.
* Support responsible and risk-aware data release.

---

## Privacy Risk Model

The project uses an equivalence-class based risk model.

### Re-identification Risk

```text
Risk = 1 / Equivalence-Class Size
```

Where the equivalence-class size represents the number of records sharing the same quasi-identifier combination.

Examples:

```text
1 matching record  → 100% risk
2 matching records → 50% risk
5 matching records → 20% risk
```

In the original dataset, the selected quasi-identifier combination produces unique records, resulting in a calculated **100% re-identification risk** for all 25 records.

---

## Attribute Classification

The dataset is analysed according to three privacy categories.

| Category            | Description                                                    | Example                           |
| ------------------- | -------------------------------------------------------------- | --------------------------------- |
| Direct Identifier   | Directly identifies an individual                              | Student ID                        |
| Quasi-Identifier    | May identify an individual when combined with other attributes | Age, Gender, PIN Code, Department |
| Sensitive Attribute | Information requiring protection from disclosure               | CGPA, Scholarship Status          |

This classification establishes which attributes should be removed, generalized, transformed, or protected.

---

## Privacy-Preserving Techniques

The project demonstrates both **non-perturbative** and **perturbative** approaches.

### Non-Perturbative Techniques

These techniques reduce the granularity or visibility of information without introducing artificial values.

#### 1. Suppression

Removes or hides identifying information.

```text
Student ID → Suppressed
560001     → 560***
```

#### 2. Generalization

Replaces precise values with broader categories.

```text
Age: 20
     ↓
Age: 20–22
```

This increases equivalence-class size and reduces uniqueness.

#### 3. Top/Bottom Coding

Protects extreme numerical values.

```text
CGPA ≥ 9.0 → ≥ 9.0
CGPA ≤ 6.5 → ≤ 6.5
```

This protects potentially identifiable outliers while preserving most of the dataset.

#### 4. Aggregation

Replaces individual records with group-level statistics.

Example:

| Department       | Students | Average CGPA | Scholarship |
| ---------------- | -------: | -----------: | ----------: |
| Computer Science |        8 |         8.45 |       62.5% |
| Electronics      |        6 |         7.63 |       33.3% |
| Mechanical       |        5 |         6.92 |       20.0% |
| Civil            |        5 |         6.62 |        0.0% |

Aggregation provides stronger privacy protection but removes individual-level information.

---

### Perturbative Techniques

Perturbative techniques modify values while attempting to retain useful statistical properties.

#### 5. Noise Addition

Controlled random noise is added to numerical values.

For CGPA:

```text
Noise range: −0.2 to +0.2
```

The objective is to prevent exact sensitive-value disclosure while retaining useful statistical characteristics.

#### 6. Data Swapping

Sensitive values are exchanged between selected records.

This breaks the direct association between an individual's record and their original sensitive value.

#### 7. Randomization

Controlled changes are introduced into categorical attributes.

The documented implementation applies randomization to scholarship status.

#### 8. Microaggregation

Records are grouped and individual numerical values are replaced with cluster-level means.

The documented analysis uses:

```text
Cluster size (k) = 5
```

This reduces individual-level value uniqueness while retaining some aggregate information.

---

## Privacy–Utility Trade-off

Privacy protection inevitably affects information utility.

The project compares each masking technique according to:

* Privacy improvement
* Re-identification risk
* Information loss
* Remaining analytical utility

| Technique         | Privacy Improvement | Information Loss | Utility  |
| ----------------- | ------------------- | ---------------- | -------- |
| Suppression       | High                | Moderate         | Moderate |
| Generalization    | High                | Low–Moderate     | Moderate |
| Top/Bottom Coding | Moderate            | Low              | High     |
| Aggregation       | Very High           | Very High        | Low      |
| Noise Addition    | Moderate            | Low              | High     |
| Data Swapping     | Moderate            | Low              | High     |
| Randomization     | Moderate            | Moderate         | Moderate |
| Microaggregation  | High                | Moderate         | Moderate |

The key engineering principle is that **privacy protection should be calibrated according to the intended use of the released dataset**.

---

## Architecture / Workflow

```text
                ┌──────────────────┐
                │   Original Data  │
                └────────┬─────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Attribute            │
              │ Classification       │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Quasi-Identifier     │
              │ Analysis             │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Re-identification   │
              │ Risk Assessment     │
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
      Non-Perturbative       Perturbative
          Masking                Masking
              │                     │
              └──────────┬──────────┘
                         ▼
              ┌─────────────────────┐
              │ Privacy–Utility     │
              │ Evaluation          │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Responsible Data    │
              │ Release             │
              └─────────────────────┘
```

---

## Security Engineering Perspective

The project follows a **defence-in-depth approach to data privacy**.

Instead of depending on a single masking mechanism, multiple techniques can be combined according to:

* Data sensitivity
* Re-identification risk
* Expected adversary knowledge
* Research requirements
* Acceptable information loss

This approach recognizes that **no single masking technique eliminates privacy risk completely**.

---

## Dataset

The project uses a **fictional university student dataset** created specifically for demonstrating privacy-preserving data publishing.

### Dataset Characteristics

```text
Records:        25
Domain:         University Student Data
Dataset Type:   Fictional
Primary Focus:  Privacy Risk & Data Masking
```

The dataset does not represent real students or real personal information.

**Do not commit real personal or sensitive information to this repository.**

---

## Security Considerations

This project is an educational privacy-engineering implementation and should not be interpreted as a guarantee of anonymity.

Potential risks include:

* External information may enable re-identification.
* Different quasi-identifier combinations may produce different risk levels.
* Masking parameters require appropriate calibration.
* Perturbation can reduce individual-level accuracy.
* Excessive masking can reduce research utility.
* Aggregation removes record-level analytical capabilities.
* Technical masking should be supported by appropriate governance and data-sharing controls.

A secure data-release process should therefore consider both **technical controls and organizational safeguards**.

---

## Privacy Engineering Principles

### Data Minimization

Release only the information necessary for the intended purpose.

### Purpose Limitation

Use data only for an authorized and clearly defined purpose.

### Re-identification Resistance

Reduce the ability to associate released records with real individuals.

### Responsible Data Sharing

Combine technical masking with appropriate policies and data-sharing controls.

### Privacy–Utility Balance

Select masking techniques according to both privacy requirements and legitimate analytical needs.

---

## Technology

The project documentation identifies the following technologies/tools:

* **Python**
* **Pandas**
* **Microsoft Excel**

The exact runtime dependencies and source-code structure should be documented according to the final repository implementation.

---

## Installation

> Update these commands according to the actual source-code structure before publishing.

```bash
git clone <repository-url>
cd privacyguard-microdata-anonymization

pip install -r requirements.txt
```

### Run

```bash
python <entry-point>.py
```

The exact entry point and dependency list should match the implementation committed to the repository.

---

## Project Structure

The final repository structure should reflect the actual implementation.

```text
privacyguard-microdata-anonymization/
│
├── README.md
├── LICENSE
├── requirements.txt
│
├── data/
│   ├── original/
│   └── masked/
│
├── src/
│   └── <project-source-files>
│
├── outputs/
│   └── <generated-results>
│
└── docs/
    └── <documentation>
```

---

## Limitations

* The dataset is fictional and relatively small.
* Risk depends on the selected quasi-identifiers.
* External datasets can introduce additional re-identification opportunities.
* Perturbative techniques can reduce individual-level accuracy.
* Aggregation significantly reduces record-level utility.
* No masking technique provides an absolute anonymity guarantee.
* Real-world deployments require a defined threat model and appropriate governance.

---

## Future Enhancements

Potential future improvements include:

* Automated privacy-risk scoring
* Configurable quasi-identifier selection
* k-anonymity validation
* l-diversity analysis
* t-closeness analysis
* Differential privacy mechanisms
* Automated privacy–utility optimization
* Adversarial re-identification testing
* Larger benchmark datasets
* Automated testing and reproducible experiments

These are proposed enhancements and are not represented as current capabilities.

---

## References

The project documentation references established privacy research and standards, including:

1. Sweeney, L. — *Simple Demographics Often Identify People Uniquely*, 2000.
2. Samarati, P. and Sweeney, L. — *Protecting Privacy When Disclosing Information*, 1998.
3. Nissenbaum, H. — *Privacy in Context*, 2010.
4. Government of India — *Digital Personal Data Protection Act, 2023*.
5. ISO/IEC 29101:2018 — *Privacy Architecture Framework*.
6. European Union — *General Data Protection Regulation (GDPR)*.

---

## License

This project is released under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the complete license text.

---

## Disclaimer

This project is intended for **academic, educational, and privacy-engineering demonstration purposes**.

The implemented techniques should not be interpreted as a guarantee that a real-world dataset is anonymous, legally compliant, or safe for unrestricted publication.

Real-world data-release decisions should consider the threat model, dataset sensitivity, intended use, applicable regulations, organizational policies, and appropriate privacy assessment procedures.

---

## Project Focus

```text
Data Privacy
Privacy Engineering
Re-identification Risk
Microdata Protection
Data Masking
Privacy–Utility Trade-off
Information Loss
Responsible Data Sharing
Cybersecurity
```
