from dotenv import load_dotenv
import pandas as pd , os , time,json
import requests

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}

# Fetch 200 popular repositories (2 pages x 100)
def get_repos():
    repos=[]
    for page in [1,2]:
        url = "https://api.github.com/search/repositories"
        params={"q": "stars:>500","sort": "stars" ,"per_page": 100 ,"page" : page
    }
        request=requests.get(url, headers=HEADERS , params=params)
        repos+= request.json()["items"]
    return repos 

# Fetch top 5 contributors of a repository
def get_contributors(owner,repo):
    url=f"https://api.github.com/repos/{owner}/{repo}/contributors"
    params={"per_page":5}
    request=requests.get(url,headers=HEADERS,params=params)
    if request.status_code!=200:
        return[]
    return request.json()

# Fetch user profile data
def get_user_data(username):
    url=f"https://api.github.com/users/{username}"
    request=requests.get(url,headers=HEADERS)
    if request.status_code!=200:
        return[]
    return request.json()

# Fetch user's own repositories
def get_user_repos(username):
    url=f"https://api.github.com/users/{username}/repos"
    params={"per_page":30 , "sort":"updated"}
    request=requests.get(url,headers=HEADERS,params=params)
    if request.status_code!=200:
        return[]
    return request.json()

def get_commit(username,owner,repo):
    url=f"https://api.github.com/repos/{owner}/{repo}/commits"
    params={"author":username , "per_page":30}
    request=requests.get(url,headers=HEADERS,params=params)
    if request.status_code!=200:
        return[]
    return request.json()

def get_files(owner,repo):
    url=f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD"
    params={"recursive": 1}
    request=requests.get(url,headers=HEADERS,params=params)
    return request.json().get("tree",[])


# Extract all features for a single user
def features(username,owner,repo):

    print(f"  → {username} ") 
    user=get_user_data(username)
    user_repos=get_user_repos(username)
    commits=get_commit(username,owner,repo)
    files =get_files(owner,repo)

    # Commit analysis
    all_commits=len(commits)
    msg_length=[] 
    night_commits=0

    for c in commits:
        try:
            msg=c["commit"]["message"]
            msg_length.append(len(msg))

            date_str = c["commit"]["author"]["date"]
            hour = int(date_str[11:13])
            if hour >= 0 and hour <= 6:
                night_commits += 1
        except:
            pass

    avg_msg_length=sum(msg_length)/len(msg_length) if msg_length else 0
    night_ratio=night_commits/all_commits if all_commits>0 else 0

    has_tests=0
    has_readme=0
    all_stars=0
    all_forks=0
    languages=set()

    # Repo analysis

    for repo_item in user_repos:
        all_stars+=repo_item.get("stargazers_count",0)
        all_forks+=repo_item.get("forks_count",0)
        if repo_item.get("language"):
            languages.add(repo_item["language"])

    paths = [f["path"].lower() for f in files if isinstance(f, dict)]
    has_tests  = int(any("test"   in p for p in paths))
    has_readme = int(any("readme" in p for p in paths))
        

    features = {
        "username": username,
        "total_commits": all_commits,
        "avg_commit_msg_length": round(avg_msg_length, 2),
        "night_commit_ratio": round(night_ratio, 2),
        "followers": user.get("followers",0),
        "following": user.get("following", 0),
        "public_repos": user.get("public_repos", 0),
        "total_stars_received": all_stars,
        "total_forks": all_forks,
        "languages_count": len(languages),
        "has_tests": has_tests,
        "has_readme": has_readme,
        "account_age_days": 0,   
    }

        # Account age

    try:
        from datetime import datetime
        created=user.get("created_at","")[:10]
        age=(datetime.now()-datetime.strptime(created,"%Y-%m-%d")).days
        features["account_age_days"] = age
    except:
        pass
    return features

all_features = []
seen = set()

for repo in get_repos():
    owner = repo["owner"]["login"]
    repo_name = repo["name"]
    for contributor in get_contributors(owner, repo_name):
        username = contributor.get("login", "")
        if username and username not in seen:
            seen.add(username)
            try:
                all_features.append(features(username, owner, repo_name))
            except:
                pass
            time.sleep(0.5)

# Save to csv
os.makedirs("data", exist_ok=True)
pd.DataFrame(all_features).to_csv("data/github_data.csv", index=False)
print(f"Finish! {len(all_features)} people ")
