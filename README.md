# World Happiness Report Analysis (2015–2023)

## 📌 Project Overview
This project explores the **World Happiness Report data (2015–2023)** using Exploratory Data Analysis (EDA) coded in Python.  
The analysis investigates the **factors influencing happiness**, regional differences, country-level trends, and global patterns over time.  

The goal is to:
- Identify the strongest drivers of happiness.
- Compare happiness trends across regions and countries.
- Visualize top and bottom countries by happiness score.
- Track global happiness changes over time.
- Offer solutions to continue improving humanity contentment and satisfaction over time. 

---

## 📂 Dataset and Methods of Approach
The Global Happiness Predictions file includes yearly observations from 2015–2023, with the following main features: Country, Region, GDP Per Capita, Social Support, Healthy Life Expectancy, Freedom to Make Life Choices, Generosity, Perceptions of Corruption and the Year distribution. Our target is the Happiness Score in countries studied. We trained several models including seasonals, regressors and neural networks, to obtain reasonable predictions but ultimately the models that perfomed the best were the simpler regressors for this particular dataset. 


## Quick start of the dashboard for interactive visualizations(conda):

1. Create the conda environment (recommended):

```powershell
conda env create -f environment.yml
conda activate smilescore
python dashboard.py
```

2. If you don't use conda, create a venv with Python 3.11, install packages with pip, then run `python dashboard.py`.

VS Code: use the Command Palette → Python: Select Interpreter to pick the env, then Run Task → "Run current Python file".
