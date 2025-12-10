# ReservoirDashboard
Interactive Havlena–Odeh Reservoir Material Balance Dashboard.

## Overview

This dashboard is an interactive analytical tool designed to perform Havlena-Odeh material balance calculations for reservoir engineering applications.

## What This Dashboard Provides

Provides estimations of:
- Original oil in place
- Gas cap in place
- Gas cap ratio

## Input Requirements

Upload an Excel file (.xlsx) containing 2 sheets.

### Sheet 1: "Production" (Required Columns)
- **Bo** - Oil FVF
- **Bg** - Gas FVF
- **Rs** - Solution GOR
- **Np** - Cumulative oil production
- **Gp** - Cumulative gas production
- **p** - Reservoir pressure

### Sheet 2: "Initial" (Required Parameters)
- **Boi** - Initial oil FVF
- **Bgi** - Initial gas FVF
- **Rsi** - Initial solution GOR

## Important Notes

- Accuracy depends on PVT and production data quality.
- The assigned sheets structure **MUST** be followed specifically, including capital and small letters such as **p** in production sheet, to avoid errors.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```
