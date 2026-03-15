import time
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import pandas as pd
from pandas import json_normalize

# Import precomputed reaction counts, case counts, and total cases per drug
from sem_adverse import reaction_counts_sema, total_cases_sema, reaction_case_counts_sema
from lira_adverse import reaction_counts_lira, total_cases_lira, reaction_case_counts_lira
from dula_adverse import reaction_counts_dula, total_cases_dula, reaction_case_counts_dula

# GLP-1 drugs and API fetch parameters
glp1_drugs = ['SEMAGLUTIDE', 'LIRAGLUTIDE', 'DULAGLUTIDE', 'EXENATIDE']
records_per_request = 100  # max per API request
total_records = 500         # total to fetch per drug

# --- FUNCTION TO FETCH DATA FROM OPENFDA ---
def fetch_faers(drug_name, total_records, batch_size=100):
    all_reports = []  # store all fetched reports
    for skip in range(0, total_records, batch_size):
        url = "https://api.fda.gov/drug/event.json"
        params = {
            "search": f"patient.drug.medicinalproduct:{drug_name}",
            "limit": batch_size,
            "skip": skip
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break  # stop if API call fails
        data = response.json()
        results = data.get('results', [])
        all_reports.extend(results)
        time.sleep(0.2)  # polite pause to avoid rate-limiting
    return all_reports

# --- FUNCTION TO FILTER PRIMARY DRUG ---
def keep_primary_drug(drug_list, drug_name):
    """Keeps only the drug where drugcharacterization == 1 (primary)"""
    for drug in drug_list:
        if drug.get("drugcharacterization") == "1" and drug_name in drug.get("medicinalproduct", "").upper():
            return drug
    return None

# --- ADD DRUG NAME TO REACTION COUNTS ---
reaction_counts_dula['drug'] = 'Dulaglutide'
reaction_counts_lira['drug'] = 'Liraglutide'
reaction_counts_sema['drug'] = 'Semaglutide'

# --- TOP 10 REACTIONS PER DRUG ---
top10_dula = reaction_counts_dula.head(10)
top10_sema = reaction_counts_sema.head(10)
top10_lira = reaction_counts_lira.head(10)

comparison_df = pd.concat([top10_dula, top10_sema, top10_lira], ignore_index=True)

# --- COMPUTE PERCENTAGE OF CASES PER REACTION ---
reaction_case_counts_dula['percentage'] = reaction_case_counts_dula['case_count'] / total_cases_dula * 100
reaction_case_counts_dula['drug'] = 'Dulaglutide'

reaction_case_counts_sema['percentage'] = reaction_case_counts_sema['case_count'] / total_cases_sema * 100
reaction_case_counts_sema['drug'] = 'Semaglutide'

reaction_case_counts_lira['percentage'] = reaction_case_counts_lira['case_count'] / total_cases_lira * 100
reaction_case_counts_lira['drug'] = 'Liraglutide'

comparison_percentage_df = pd.concat(
    [reaction_case_counts_dula, reaction_case_counts_sema, reaction_case_counts_lira],
    ignore_index=True
)

# Sort by drug and case_count
comparison_percentage_df = comparison_percentage_df.sort_values(['drug', 'case_count'], ascending=[True, False]).reset_index(drop=True)

# Filter out minor reactions (<2% of cases)
filtered_df = comparison_percentage_df[comparison_percentage_df['percentage'] >= 2]

# Sort by drug and percentage for plotting
filtered_df = filtered_df.sort_values(['drug', 'percentage'], ascending=[True, False]).reset_index(drop=True)

# Keep top 10 per drug for barplot / heatmap
top10_filtered = filtered_df.groupby('drug').head(10)

print(top10_filtered)


plt.figure(figsize=(12, 10))
# sns.barplot(
#     data=top10_filtered,
#     x='percentage',
#     y='reaction_term',
#     hue='drug'
# )
# plt.title('Top Adverse Reactions for GLP-1 Drugs')
# plt.xlabel('Percentage of Cases (%)')
# plt.ylabel('Adverse Reactions')
# plt.tight_layout()
#
#
# g = sns.catplot(
#     data=top10_filtered,
#     x="percentage",
#     y="reaction_term",
#     col="drug",
#     kind="bar",
#     height=6,
#     aspect=0.9,
#     sharex=False
# )
#
# g.set_titles("{col_name}")
# g.set_axis_labels("Percentage of Cases (%)", "Adverse Reaction")
# top10_filtered['reaction_term'] = top10_filtered['reaction_term'].str.title()
# plt.tight_layout()
# plt.show()
# plt.show()


# -----------------------------
# --- HEATMAP ---
# -----------------------------
# Reorder reactions so top reactions are on top
reaction_order = top10_filtered.groupby('reaction_term')['percentage'].max().sort_values(ascending=False).index

# Pivot data for heatmap: rows=reactions, columns=drugs, cells=percentage
heatmap_data = top10_filtered.pivot(
    index='reaction_term',
    columns='drug',
    values='percentage'
).reindex(reaction_order).fillna(0)

plt.figure(figsize=(10, 8))
sns.heatmap(
    heatmap_data,
    annot=True,           # show values
    fmt=".1f",            # one decimal
    cmap='viridis',       # color palette
    cbar_kws={'label': 'Percentage of Cases (%)'}
)

plt.title('Top Adverse Reactions Across GLP-1 Drugs')
plt.xlabel("Drug")
plt.ylabel("Adverse Reactions")
plt.tight_layout()
plt.show()