from itertools import groupby
import pandas as pd
import ast
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.pyplot import title
import textwrap
import matplotlib.patches as mpatches


df = pd.read_excel("final_sema_report.xlsx")
# print(df.columns)

#Convert string lists to python lists
df['reaction_term'] = df['reaction_term'].apply(ast.literal_eval)
df['reaction_outcome'] = df['reaction_outcome'].apply(ast.literal_eval)

def pad_severity(row):
    diff = len(row['reaction_term']) - len(row['reaction_outcome'])
    if diff > 0 :
        return row['reaction_outcome'] + [None] * diff
    return row['reaction_outcome']

df['reaction_outcome'] = df.apply(pad_severity, axis=1)


# TO GET THE LENGTH OF EACH ROW IN THE REACTION-TERM
# df['rt_len'] = df['reaction_term'].apply(len)
# print(df['rt_len'])
#
# df['ro_len'] = df['reaction_outcome'].apply(len)
# print(df['ro_len'])

#RETURNS THE ROWS WHERE THERE IS LENGTH DIFFERENCE
# length_diff = df[df['rt_len'] != df['ro_len']][
#     ['safetyreportid', 'rt_len', 'ro_len']
# ]

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

exploded_reaction_data = df.explode(['reaction_term', 'reaction_outcome'])

adverse_data = exploded_reaction_data[['safetyreportid', 'medicinalproduct','reaction_term', 'reaction_outcome']].copy()
adverse_data['reaction_outcome'] = adverse_data['reaction_outcome'].map(outcome_map)

reaction_counts = (
    adverse_data
    .groupby('reaction_term')
    .size()
    .reset_index(name='report_count')
    .sort_values('report_count', ascending=False)
)

total_reaction_count = adverse_data.shape[0]
# print(f"total reaction count: {total_reaction_count}")

total_cases_sema = adverse_data['safetyreportid'].nunique()
# print(f"total cases: {total_cases_sema}")

reaction_case_counts_sema = (
    adverse_data
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='case_count')
    .sort_values('case_count', ascending=False)
)

print(f"total cases: {reaction_case_counts_sema}")
print(reaction_counts.head(10))

reaction_counts_sema = reaction_counts.copy()
reaction_outcome_counts = (
    adverse_data
    .groupby('reaction_outcome')
    .size()
    .reset_index(name='outcome_count')
    .sort_values('outcome_count', ascending=False)
)


top10 = reaction_outcome_counts.head(10)

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

#	•	pct = percentage of each slice
#	•	If percentage > 2% → show it
#	•	If ≤ 2% → hide it

# def autopct_format(pct):
#     return ('%1.1f%%' % pct) if pct > 2 else ''  # hide <2%
#

# wedges, texts, autotexts = plt.pie(
#     top10['outcome_count'],
#     autopct=autopct_format,
#     startangle=140,
#     colors=colors,
#     pctdistance=0.7,
#     textprops={'fontsize': 10}
# )
#
# plt.legend(
#     wedges,
#     [f"{label} ({count})" for label, count in zip(top10['reaction_outcome'], top10['outcome_count'])],
#     title="Reaction Outcome",
#     loc="center left",
#     bbox_to_anchor=(1, 0.5),
#     fontsize=10,
#     title_fontsize=11
# )
#
# plt.title("Distribution of Reported Outcomes for Semaglutide")
# plt.tight_layout()
# plt.show()
#

#REACTIONS THAT LEAD TO DEATH
death_data = adverse_data[adverse_data['reaction_outcome'] == 'Death']
death_counts = (
    death_data
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='unique_death_reports')
    .sort_values('unique_death_reports', ascending=False)
)

top_deaths = death_counts.head(10)



severe_reactions = death_data[~death_data['reaction_term'].isin(minor_reactions)]
severe_reactions_count = (
    severe_reactions
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='count')
    .sort_values('count', ascending=False)
)
plt.figure(figsize=(10,6))

top_severe_counts = severe_reactions_count.head(10)
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

# plt.xlabel('Number of reports')
# plt.ylabel('Reaction Terms')
# plt.title('Top 10 Severe Reactions Reported in Fatal Cases Associated with Semaglutide')
# plt.tight_layout()
# plt.show()

# sns.barplot(
#     x='unique_death_reports',
#     y='reaction_term',
#     data=top_deaths,
#     palette='viridis'
# )
# ax = plt.gca()
# wrapped_labels = [
#     "\n".join(textwrap.wrap(label.get_text(), width=25))
#     for label in ax.get_yticklabels()
# ]
# ax.set_yticklabels(wrapped_labels, fontsize=6)
# plt.xticks(fontsize=10, rotation=0)
#
# plt.title('Top 10 Reactions Associated With Semaglutide Leading to Death')
# plt.xlabel('Reaction Term')
# plt.ylabel('Number of Deaths')
# plt.show()


#HORIZONTAL BAR CHART USING SEABORN
# plt.figure(figsize=(10,6))
# sns.barplot(
#     x='report_count',
#     y='reaction_term',
#     data=top10,
#     palette='viridis'
# )

# plt.title('Top 10 Most Reported Reactions for Semaglutide')
# plt.xlabel('Number of Reports')
# plt.ylabel('Adverse Event')
# plt.tight_layout()
# plt.show()

#VERTICAL BAR CHART USING MATPLOTLIB
# plt.figure(figsize=(8,5))
# plt.bar(top10['reaction_term'], top10['report_count'], color='skyblue')
# plt.xticks(rotation=45, ha='right')
# plt.title("Top 10 Most Reported Reactions for Semaglutide")
# plt.xlabel('Adverse Event')
# plt.ylabel('Number of Reports')
# plt.tight_layout()
# plt.show()


