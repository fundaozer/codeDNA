import pandas as pd ,joblib ,os
from sklearn.ensemble import GradientBoostingClassifier , IsolationForest
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

df = pd.read_csv("data/github_data_labeled.csv")

FEATURES = [
    "total_commits", "avg_commit_msg_length", "night_commit_ratio", "followers","following",
    "public_repos", "total_stars_received","total_forks","languages_count", "has_tests", "has_readme", "account_age_days"]

X=df[FEATURES].fillna(0)
y=df["label"]

X_train, X_test, y_train, y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)

scaler=StandardScaler()
X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)

model=GradientBoostingClassifier(n_estimators=100 ,random_state=42)
model.fit(X_train,y_train)
print(classification_report(y_test,model.predict(X_test)))

cv = cross_val_score(model, X_train, y_train, cv=5)
print(f"Cross-Validation: {cv.mean():.2f} ± {cv.std():.2f}")

risk_model = IsolationForest(contamination=0.1, random_state=42)
risk_model.fit(X_train)

os.makedirs("models", exist_ok=True)
joblib.dump(model,      "models/model.pkl")
joblib.dump(scaler,     "models/scaler.pkl")
joblib.dump(risk_model, "models/risk_model.pkl")
print("Models saved!")


# Model Performance Results
# -------------------------------------------------------
#              precision    recall  f1-score   support
# junior          0.97      0.86      0.91        36
# mid             0.92      0.97      0.94        79
# senior          0.99      0.97      0.98        68
# accuracy                            0.95       183
# macro avg       0.96      0.94      0.94       183
# weighted avg    0.95      0.95      0.95       183
# -------------------------------------------------------
