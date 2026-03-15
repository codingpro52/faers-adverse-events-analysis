import ast

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import textwrap

from matplotlib.pyplot import viridis

df = pd.read_excel('final_lira_report.xlsx')


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

df['reaction_outcome'] = df['reaction_outcome'].apply(ast.literal_eval)
df['reaction_term'] = df['reaction_term'].apply(ast.literal_eval)

#
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

total_cases_lira = adverse_data['safetyreportid'].nunique()
print(f"total cases: {total_cases_lira}")
reaction_case_counts_lira = (
    adverse_data
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='case_count')
    .sort_values('case_count', ascending=False)
)

print(f"total cases: {reaction_case_counts_lira}")
reaction_count = (
    adverse_data
    .groupby('reaction_term')
    .size()
    .reset_index(name='report_count')
    .sort_values('report_count', ascending=False)
)

print(reaction_count.head(10))
reaction_counts_lira = reaction_count.copy()

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
plt.figure(figsize=(10,6))
#DISTRIBUTION OF REPORTED OUTCOMES DISPLAYED IN PIE CHART
#
# def autopct_format(pct):
#     return ('%1.1f%%' % pct) if pct > 2 else ''  # hide <2%
#
#
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
#     title='Reaction Outcome',
#     loc='center left',
#     bbox_to_anchor=(1, 0.5),
#     fontsize=10,
#     title_fontsize=11,
# )
# plt.title("Distribution of Reported Outcomes for Liraglutide")
# plt.tight_layout()
# plt.show()



#DISTRIBUTION OF REPORTED OUTCOMES DISPLAYED IN BAR CHART
# sns.barplot(
#     x='outcome_count',
#     y='reaction_outcome',
#     data=top10,
#     palette=colors
# )


# legend_patches = [
#     mpatches.Patch(color=color_map[outcome], label=outcome)
#     for outcome in top10['reaction_outcome']
#     if outcome in color_map
# ]

# plt.legend(
#     handles=legend_patches,
#     title="Reported Outcomes",
#     bbox_to_anchor=(1, 1),
#     loc='upper left',
# )
#

# plt.xlabel('Number of Reports')
# plt.ylabel('Adverse Events')
# plt.title('Distribution of Reported Outcomes for Liraglutide')
# plt.tight_layout()
# plt.show()


#REACTIONS ASSOCIATED WITH DEATH
death_data = adverse_data[adverse_data['reaction_outcome'] == 'Death']
death_counts = (
    death_data
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='unique_death_reports')
    .sort_values('unique_death_reports', ascending=False)

)



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
# plt.title('Top 10 Reactions Associated With Liraglutide Leading to Death')
# plt.xlabel('Reaction Term')
# plt.ylabel('Number of Deaths')
# plt.show()

# nausea_death = death_data[death_data['reaction_term'] == 'Nausea']
# nausea_death = nausea_death['safetyreportid'].unique()
# co_reactions = death_data[death_data['safetyreportid'].isin(nausea_death)]
# co_reactions_counts = (
#     co_reactions
#     .groupby('reaction_term')
#     .size()
#     .reset_index(name='count')
#     .sort_values('count', ascending=False)
# )

severe_reactions = death_data[~death_data['reaction_term'].isin(minor_reactions)]
severe_counts = (
    severe_reactions
    .groupby('reaction_term')['safetyreportid']
    .nunique()
    .reset_index(name='count')
    .sort_values('count', ascending=False)
)
print(severe_counts)
top_severe_counts = severe_counts.head(10)
plt.figure(figsize=(10,6))



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
# plt.title('Top 10 Severe Reactions Reported in Fatal Cases Associated with Liraglutide')
# plt.tight_layout()
# plt.show()

