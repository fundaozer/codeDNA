import requests, pandas as pd, joblib, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
HEADERS = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}

FEATURES = ["total_commits", "avg_commit_msg_length", "night_commit_ratio",
            "followers", "following", "public_repos", "total_stars_received",
            "total_forks", "languages_count", "has_tests", "has_readme", "account_age_days"]

model      = joblib.load("models/model.pkl")
scaler     = joblib.load("models/scaler.pkl")
risk_model = joblib.load("models/risk_model.pkl")

def get_features(username, owner, repo):
    user       = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS).json()
    commits    = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits",
                              headers=HEADERS, params={"author": username, "per_page": 30}).json()
    user_repos = requests.get(f"https://api.github.com/users/{username}/repos",
                               headers=HEADERS, params={"per_page": 30}).json()
    files      = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD",
                               headers=HEADERS, params={"recursive": 1}).json().get("tree", [])

    msgs, nights = [], 0
    for c in commits:
        try:
            msgs.append(len(c["commit"]["message"]))
            if int(c["commit"]["author"]["date"][11:13]) <= 6:
                nights += 1
        except: pass

    total = len(commits)
    all_stars, all_forks, languages = 0, 0, set()
    for r in user_repos:
        all_stars += r.get("stargazers_count", 0)
        all_forks += r.get("forks_count", 0)
        if r.get("language"):
            languages.add(r["language"])

    paths      = [f["path"].lower() for f in files if isinstance(f, dict)]
    has_tests  = int(any("test"   in p for p in paths))
    has_readme = int(any("readme" in p for p in paths))

    age = 0
    try:
        created = user.get("created_at", "")[:10]
        age = (datetime.now() - datetime.strptime(created, "%Y-%m-%d")).days
    except: pass

    return {
        "total_commits":          total,
        "avg_commit_msg_length":  round(sum(msgs)/len(msgs), 2) if msgs else 0,
        "night_commit_ratio":     round(nights/total, 2) if total else 0,
        "followers":              user.get("followers", 0),
        "following":              user.get("following", 0),
        "public_repos":           user.get("public_repos", 0),
        "total_stars_received":   all_stars,
        "total_forks":            all_forks,
        "languages_count":        len(languages),
        "has_tests":              has_tests,
        "has_readme":             has_readme,
        "account_age_days":       age,
    }

def predict(repo_url):
    parts        = repo_url.rstrip("/").split("/")
    owner, repo  = parts[-2], parts[-1]
    username = owner
    feat     = get_features(username, owner, repo)
    X        = pd.DataFrame([feat])[FEATURES].fillna(0)
    Xs       = scaler.transform(X)
    level    = model.predict(Xs)[0]
    proba    = dict(zip(model.classes_, model.predict_proba(Xs)[0]))
    risk     = float(risk_model.decision_function(Xs)[0])

    return {
        "username": username,
        "level":    level,
        "confidence": max(proba.values()),
        "proba":    proba,
        "risk":     risk,
        "features": feat
    }