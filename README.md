# 🧬 CodeDNA — AI Developer Personality Analyzer

CodeDNA analyzes GitHub repositories to predict a developer's experience level 
and risk profile using machine learning trained on 914 real GitHub profiles.

## Features
- Junior / Mid / Senior classification
- Risk score via anomaly detection (Isolation Forest)
- Skill radar chart across 6 dimensions
- 12 behavioral metrics extracted from GitHub API

## Tech Stack
- Python, scikit-learn, Streamlit, Plotly
- Gradient Boosting Classifier (95% accuracy, F1: 0.94)
- Isolation Forest for risk detection
- GitHub REST API v3

## Model Performance
| Class    | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| Junior   | 0.97      | 0.86   | 0.91     |
| Mid      | 0.92      | 0.97   | 0.94     |
| Senior   | 0.99      | 0.97   | 0.98     |
| Accuracy |           |        | 0.95     |
