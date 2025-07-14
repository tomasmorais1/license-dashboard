# MS License Dashboard

A Streamlit-based dashboard for visualizing and analyzing Microsoft licensing costs by company and license type.

## 🔧 Features

- Upload CSV file with user and license data
- Automatic cost calculation based on customizable license prices
- Simulate unassigned licenses
- Summary tables for costs and quantities
- Interactive charts using Plotly
- Custom CSS styling for clean visuals

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tomasmorais1/license-dashboard.git
cd license-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

Then open in your browser: [http://localhost:8501](http://localhost:8501)

## 📄 CSV File Format

The uploaded CSV should be structured like this (semicolon `;` separated):

```
Email;Company;License1;License2;License3;...
```

### Example:

```
john.doe@example.com;Company;SPE_E3;EMS
```

## 🧠 Notes

- License costs can be modified in the sidebar and saved locally to a JSON file.
- Some company names are automatically grouped using a predefined mapping.
- Unassigned licenses (e.g., accounting purposes) can be simulated and included in the analysis.

## 📦 Requirements

- Python 3.8+
- `streamlit`
- `pandas`
- `plotly`

You can install all requirements using:

```bash
pip install -r requirements.txt
```

## 📸 Preview

---

Feel free to open an issue or pull request if you find bugs or want to contribute.
