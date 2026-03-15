import pandas as pd
import numpy as np
import ast
import json
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap
import matplotlib.patches as mpatches


df = pd.read_excel('final_dula_report.xlsx')

outcome_map = {
    '1': 'Death',
    '2': 'Life-threatening',
    '3': 'Hospitalisation',
    '4': 'Disability',
    '5': 'Congenital anomaly',
    '6': 'Other serious',
    None: 'Not reported'
}

minor_reactions = [
    'Nausea',
    'Vomiting',
    'Abdominal pain upper',
    'Abdominal pain',
    'Dizziness',
    'Back pain',
    'Diarrhoea',
    'Headache'
]




df['reaction_term'] = df['reaction_term'].apply(ast.literal_eval)
df['reaction_outcome'] = df['reaction_outcome'].apply(ast.literal_eval)



def pad_severity(row):
    diff = len(row['reaction_term']) - len(row['reaction_outcome'])
    if diff > 0:
        return row['reaction_outcome'] + [None] * diff
    return row['reaction_outcome']

df['reaction_outcome'] = df.apply(pad_severity, axis=1)
exploded_reaction_data = df.explode(['reaction_term', 'reaction_outcome'])
# print(exploded_reaction_data.head(10))
adverse_data = exploded_reaction_data[['safetyreportid' , 'medicinalproduct','reaction_term', 'reaction_outcome']].copy()
adverse_data['reaction_outcome'] = adverse_data['reaction_outcome'].map(outcome_map)


total_cases_dula = adverse_data['safetyreportid'].nunique()
print(f"total cases: {total_cases_dula}")
reaction_case_counts_dula = (
    adverse_data
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='case_count')
    .sort_values('case_count', ascending=False)
)

print(f"total cases: {reaction_case_counts_dula}")
reaction_count = (
    adverse_data
    .groupby('reaction_term')
    .size()
    .reset_index(name='report_count')
    .sort_values('report_count', ascending=False)
)
print(reaction_count.head(10))

reaction_counts_dula = reaction_count.copy()

reaction_outcome_counts = (
    adverse_data
    .groupby('reaction_outcome')
    .size()
    .reset_index(name='outcome_count')
    .sort_values('outcome_count', ascending=False)
)
top10 = reaction_outcome_counts.head(10)
# print(top10.head(10))

color_map = {
    'Death': 'red',
    'Life-threatening': 'darkred',
    'Hospitalisation': 'orange',
    'Disability': 'purple',
    'Congenital anomaly': 'green',
    'Other serious': 'blue',
    'Not reported': 'grey'
}

colors = [color_map.get(outcome, 'gray') for outcome in top10['reaction_outcome']]
plt.figure(figsize=(10,6))
#DISTRIBUTION OF REPORTED OUTCOMES DISPLAYED IN PIE CHART

def autopct_format(pct):
    return ('%1.1f%%' % pct) if pct > 2 else ''  # hide <2%



wedges, texts, autotexts = plt.pie(
    top10['outcome_count'],
    autopct=autopct_format,
    startangle=140,
    colors=colors,
    pctdistance=0.7,
    textprops={'fontsize': 10}
)

plt.legend(
    wedges,
    [f"{label} ({count})" for label, count in zip(top10['reaction_outcome'], top10['outcome_count'])],
    title='Reaction Outcome',
    loc='center left',
    bbox_to_anchor=(1, 0.5),
    fontsize=10,
    title_fontsize=11,
)
plt.title("Distribution of Reported Outcomes for Dulaglutide")
plt.tight_layout()
plt.show()


#DISTRIBUTION OF REPORTED OUTCOMES DISPLAYED IN BAR CHART
# sns.barplot(
#     x='outcome_count',
#     y='reaction_outcome',
#     data=top10,
#     palette=colors
# )
#
#
# legend_patches = [
#     mpatches.Patch(color=color_map[outcome], label=outcome)
#     for outcome in top10['reaction_outcome']
#     if outcome in color_map
# ]
#
# plt.legend(
#     handles=legend_patches,
#     title="Reported Outcomes",
#     bbox_to_anchor=(1, 1),
#     loc='upper left',
# )
#
#
# plt.xlabel('Number of Reports')
# plt.ylabel('Adverse Events')
# plt.title('Distribution of Reported Outcomes for Dulaglutide')
# plt.tight_layout()
# plt.show()
#


death_data = adverse_data[adverse_data['reaction_outcome'] == 'Death']
death_data_count = (
    death_data
    .groupby('reaction_term')
    .size()
    .reset_index(name='report_count')
    .sort_values('report_count', ascending=False)
)


# print(death_data_count.head(10))
severe_reactions = death_data[~death_data['reaction_term'].isin(minor_reactions)]

severe_reactions_count = (
    severe_reactions
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='count')
    .sort_values('count', ascending=False)
)

top_severe_counts = severe_reactions_count.head(10)
print(f"top_severe_counts: {top_severe_counts}")
sns.barplot(
    data=top_severe_counts,
    x='count',
    y='reaction_term',
    palette='viridis'
)

palette_colors = sns.color_palette("viridis", n_colors=len(top_severe_counts))

legend_patches = [
    mpatches.Patch(color=color, label = term)
    for term, color in zip(top_severe_counts['reaction_term'], palette_colors)
]
ax = plt.gca()
ax.legend(handles=legend_patches, title='Reaction Term', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8, title_fontsize=8)
#
# plt.xlabel('Number of reports')
# plt.ylabel('Reaction Terms')
# plt.title('Top 10 Severe Reactions Reported in Fatal Cases Associated with Dulaglutide')
# plt.tight_layout()
# plt.show()


#COUNT PERCENTAGE OF NAUSEA CASES ASSOCAITED WITH DEATH
data_case_ids = df.loc[
    df['reaction_outcome'].apply(lambda x: '1' in x if isinstance(x, list) else False),
    'safetyreportid'
].reset_index(name='case_id')

nausea_ids = df.loc[
    df['reaction_term'].apply(lambda x: 'Nausea' in x),
    'safetyreportid'
].reset_index(name='nausea_id')
print(nausea_ids.head(10))

final_nausea_ids = data_case_ids['case_id'].isin(nausea_ids['nausea_id'])
final_nausea_count = final_nausea_ids.sum()


total_death_cases = len(data_case_ids)
print(f"total_death_cases: {total_death_cases}")
percent_nausea = final_nausea_count/total_death_cases*100
print(f"percent_nausea = {percent_nausea}")
