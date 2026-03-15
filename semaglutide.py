from main import fetch_faers, total_records, keep_primary_drug
import pandas as pd
from pandas import json_normalize
import ast




semaglutide_reports = fetch_faers(
    drug_name="SEMAGLUTIDE",
    total_records=total_records,
    batch_size=100
)

#coverts the reports into dataframe
sem_df = pd.DataFrame(semaglutide_reports)
#SEMAGLUTIDE DATA
sem_df["semaglutide_primary_drug"] = sem_df["patient"].apply(
    lambda p: keep_primary_drug(p["drug"], "SEMAGLUTIDE")
)
#removes empty or null entries
sem_df = sem_df[sem_df["semaglutide_primary_drug"].notnull()]

#generate a copy of the data
sem_primary_df = sem_df.copy()
drug_list = sem_primary_df["semaglutide_primary_drug"].tolist()

#this combines the safety_report_id and data where semaglutide is a primary drug
sem_df_flat = pd.concat(
    [
        sem_primary_df[["safetyreportid"]].reset_index(drop=True),
        json_normalize(drug_list)
    ],
    axis=1
)

#SEMAGLUTIDE ADVERSE REACTIONS DATA
sem_reactions_df = sem_df.copy()
#used to get the reactions data from the whole data
sem_reactions_df["reactions"] = sem_reactions_df["patient"].apply(
    lambda p:p.get("reaction", [])
)
#take each reaction and convert it into single row
sem_reactions_df = sem_reactions_df.explode("reactions")

#here we convert the reactions dataset into excel sheet
sem_reactions_df.to_excel("exploded_data.xlsx")


sem_reactions_df["reaction_term"] = sem_reactions_df["reactions"].apply(
    lambda r:r.get("reactionmeddrapt") if isinstance(r, dict) else None
)

sem_reactions_df["reaction_outcome"] = sem_reactions_df["reactions"].apply(
    lambda r: r.get("reactionoutcome") if isinstance(r, dict) else None
)

reactions_per_report = (
    sem_reactions_df
    .groupby("safetyreportid")
    .agg({"reaction_term": lambda x: list(x.dropna()),
          "reaction_outcome": lambda x: list(x.dropna())
    })
    .reset_index()
)


# FINAL REPORT CONTAINING THE DATA WHERE SEMAGLUTIDE WAS A PRIMARY DRUG ALONG WITH THE ADVERSE REACTION RELATED WITH IT
final_sema_report = sem_df_flat.merge(
    reactions_per_report,
    on="safetyreportid",
    how="left"
)


