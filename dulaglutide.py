from main import fetch_faers, keep_primary_drug, total_records
import pandas as pd
from pandas import json_normalize


dulaglutide_reports = (fetch_faers
    (
        drug_name="DULAGLUTIDE",
        total_records=total_records,
        batch_size=100
    ))

#CONVERTING THE DULAGLUTIDES DATA INTO DATAFRAME
dula_df = pd.DataFrame(dulaglutide_reports)

#CREATING A NEW COLUMN NAMED dulaglutideprimarydrug and exctracting the data
# where dulaglutide is a primary drug
dula_df["dulaglutide_primary_drug"] = dula_df["patient"].apply(
    lambda p: keep_primary_drug(p["drug"], "DULAGLUTIDE")
)

#keeping the columns that are not null/empty
dula_df = dula_df[dula_df["dulaglutide_primary_drug"].notnull()]
dula_primary_df = dula_df.copy()

drug_list = dula_primary_df["dulaglutide_primary_drug"].tolist()

dula_df_flat = pd.concat(
    [
        dula_primary_df[["safetyreportid"]].reset_index(drop=True),
        json_normalize(drug_list)
    ],
    axis=1
)
dula_df_reactions = dula_df.copy()

#REACTION PART
dula_df_reactions["reactions"] = dula_df_reactions["patient"].apply(
    lambda r: r.get("reaction", [])
)

dula_df_reactions = dula_df_reactions.explode("reactions")

if "reaction_term" not in dula_df_reactions.columns:
    dula_df_reactions["reaction_term"] = dula_df_reactions["reactions"].apply(
        lambda x: x.get("reactionmeddrapt") if isinstance(x, dict) else None
    )
dula_df_reactions["reaction_outcome"] = dula_df_reactions["reactions"].apply(
    lambda r: r.get("reactionoutcome") if isinstance(r, dict) else None
)

dula_reactions_per_report = (
    dula_df_reactions
    .groupby("safetyreportid")
    .agg({"reaction_term":lambda x :list(x.dropna()),
          "reaction_outcome": lambda x:list(x.dropna())
          })
    .reset_index()
)


dula_reactions_per_report.to_excel('dula_reactions_report.xlsx')
final_dula_report = dula_df_flat.merge(
    dula_reactions_per_report,
    on="safetyreportid",
    how="left"
)

final_dula_report.to_excel('final_dula_report.xlsx')