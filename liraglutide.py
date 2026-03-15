from main import fetch_faers, total_records, keep_primary_drug
import pandas as pd
from pandas import json_normalize


liraglutide_reports = fetch_faers(
    drug_name="LIRAGLUTIDE",
    total_records=total_records,
    batch_size=100
)
lira_df = pd.DataFrame(liraglutide_reports)

#LIRAGLUTIDE DATA
lira_df["liraglutide_primary_drug"] = lira_df["patient"].apply(
    lambda p: keep_primary_drug(p["drug"], "LIRAGLUTIDE")
)

#DOUBLE BRACKETS FIRST ONE SELECT EACH COLUMN AND FIND THE EMPTY ONES AND THEN SECOND
# TO FILTER THE ROW TO DROP IT IF EMPTY
lira_df = lira_df[lira_df["liraglutide_primary_drug"].notnull()]

lira_primary_df = lira_df.copy()

# print(lira_primary_df)
drug_list = lira_primary_df["liraglutide_primary_drug"].tolist()
# print(drug_list)
# it normalizes the df converts each key into flatten row
lira_df_flat = pd.concat(
    [
    lira_primary_df[["safetyreportid"]].reset_index(drop=True),
    json_normalize(drug_list)
    ],
    axis=1
)
# print(f"df_flat: {sem_df_flat}")
lira_df_flat.to_excel("liraglutide_primary.xlsx")

#LIRAGLUTIDE REACTION REPORT
lira_reaction_df = lira_df.copy()
lira_reaction_df["reactions"] = lira_reaction_df["patient"].apply(
    lambda p: p.get("reaction", [])
)

lira_reaction_df = lira_reaction_df.explode("reactions")

lira_reaction_df["reaction_term"] = lira_reaction_df["reactions"].apply(
    lambda r: r.get("reactionmeddrapt") if isinstance(r, dict) else None
)

lira_reaction_df["reaction_outcome"] = lira_reaction_df["reactions"].apply(
    lambda r: r.get("reactionoutcome") if isinstance(r, dict) else None
)

lira_reactions_per_report = (
    lira_reaction_df
    .groupby("safetyreportid")
    .agg({
        "reaction_term": lambda x: list(x.dropna()),
        "reaction_outcome": lambda x: list(x.dropna())
    })
    .reset_index()
)

lira_reactions_per_report.to_excel('lira_reaction_per_report.xlsx')

final_lira_report = lira_df_flat.merge(
    lira_reactions_per_report,
    on="safetyreportid",
    how="left"
)

print(final_lira_report['reaction_outcome'])
final_lira_report.to_excel("final_lira_report.xlsx")

