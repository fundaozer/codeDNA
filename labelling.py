import pandas as pd

df = pd.read_csv("data/github_data.csv")

# Calculate score
def score(row):
    s = 0
    s += min(row["total_commits"] / 4,  25)   # max 25
    s += min(row["followers"] / 10,     20)   # max 20
    s += min(row["total_stars_received"] / 20,         15)   # max 15
    s += min(row["account_age_days"] / 100,  15)   # max 15
    s += min(row["avg_commit_msg_length"] / 5, 10)   # max 10
    s += row["has_tests"] * 10                # 10
    s += min(row["languages_count"], 5)             # max 5
    return round(s, 1)

df["score"] = df.apply(score, axis=1)
df["label"] = df["score"].apply(lambda s: "junior" if s < 50 else ("mid" if s < 72 else "senior"))

print(df["label"].value_counts())

# Save to csv
df.to_csv("data/github_data_labeled.csv", index=False)
print("Labelling is over!")