import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="UN Peacekeeping Operations Analysis", layout="wide")

# Load and preprocess data
def load_data():
    data_url = "https://api.psdata.un.org/public/data/DPPADPOSS-PKO/CSV"
    df = pd.read_csv(data_url)
    date_columns = ['start_date', 'end_date', 'last_update']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df['mission_duration'] = (df['end_date'] - df['start_date']).dt.days
    return df

st.title('UN Peacekeeping Operations Analysis')
st.write('An in-depth analysis of United Nations Peacekeeping Operations')

# Load data
peace_conflict = load_data()

# 1. Overview of Peacekeeping Operations
st.header('1. Overview of Peacekeeping Operations')
total_missions = len(peace_conflict)
active_missions = peace_conflict[peace_conflict['mission_isactive'] == 'Yes'].shape[0]
inactive_missions = total_missions - active_missions

st.write(f"Total number of missions: {total_missions}")
st.write(f"Active missions: {active_missions}")
st.write(f"Inactive missions: {inactive_missions}")

# Visualization: Active vs Inactive Missions
active_inactive_df = pd.DataFrame({
    'Status': ['Active', 'Inactive'],
    'Count': [active_missions, inactive_missions]
})
chart = alt.Chart(active_inactive_df).mark_bar().encode(
    x='Status',
    y='Count',
    color='Status'
).properties(title="Active vs Inactive Missions")
st.altair_chart(chart, use_container_width=True)

# 2. Mission Duration Analysis
st.header('2. Mission Duration Analysis')
avg_duration = peace_conflict['mission_duration'].mean()
median_duration = peace_conflict['mission_duration'].median()
longest_mission = peace_conflict.loc[peace_conflict['mission_duration'].idxmax()]
shortest_mission = peace_conflict.loc[peace_conflict['mission_duration'].idxmin()]

st.write(f"Average mission duration: {avg_duration:.2f} days ({avg_duration/365:.2f} years)")
st.write(f"Median mission duration: {median_duration:.2f} days ({median_duration/365:.2f} years)")
st.write(f"Longest mission: {longest_mission['mission_acronym']} ({longest_mission['mission_duration']} days)")
st.write(f"Shortest mission: {shortest_mission['mission_acronym']} ({shortest_mission['mission_duration']} days)")

# Visualization: Distribution of Mission Durations
chart = alt.Chart(peace_conflict).mark_bar().encode(
    alt.X("mission_duration", bin=alt.Bin(maxbins=20), title="Mission Duration (days)"),
    y='count()',
).properties(title="Distribution of Mission Durations")
st.altair_chart(chart, use_container_width=True)

# 3. Geographical Analysis
st.header('3. Geographical Analysis')
location_counts = peace_conflict['mission_location'].value_counts().reset_index()
location_counts.columns = ['mission_location', 'count']

st.write("Top 10 Mission Locations:")
st.write(location_counts.head(10))

# Visualization: Top 10 Mission Locations
chart = alt.Chart(location_counts.head(10)).mark_bar().encode(
    x='count:Q',
    y=alt.Y('mission_location:N', sort='-x'),
).properties(title="Top 10 Mission Locations")
st.altair_chart(chart, use_container_width=True)

# 4. Lead Department Analysis
st.header('4. Lead Department Analysis')
dept_counts = peace_conflict['lead_department'].value_counts().reset_index()
dept_counts.columns = ['lead_department', 'count']

st.write("Missions by Lead Department:")
st.write(dept_counts)

# Visualization: Missions by Lead Department
chart = alt.Chart(dept_counts).mark_bar().encode(
    x='count:Q',
    y=alt.Y('lead_department:N', sort='-x'),
).properties(title="Missions by Lead Department")
st.altair_chart(chart, use_container_width=True)

# 5. Timeline Analysis
st.header('5. Timeline Analysis')
peace_conflict['year'] = peace_conflict['start_date'].dt.year
missions_per_year = peace_conflict.groupby('year').size().reset_index(name='count')

# Visualization: Missions Started per Year
chart = alt.Chart(missions_per_year).mark_line().encode(
    x='year:O',
    y='count:Q'
).properties(title="Number of Missions Started per Year")
st.altair_chart(chart, use_container_width=True)

# 6. Conclusion and Insights
st.header('6. Conclusion and Insights')
st.write(f"""
Based on the analysis of UN Peacekeeping Operations data, we can draw the following insights:

1. **Mission Activity**: Out of {total_missions} total missions, {active_missions} are currently active, representing {active_missions/total_missions:.2%} of all missions. This indicates a significant ongoing peacekeeping effort by the UN.

2. **Mission Duration**: The average mission duration is approximately {avg_duration/365:.2f} years, with a median of {median_duration/365:.2f} years. This suggests that peacekeeping operations often require long-term commitments. The wide range between the shortest and longest missions (from {shortest_mission['mission_duration']} days to {longest_mission['mission_duration']} days) indicates the diverse nature of peacekeeping needs across different regions and conflicts.

3. **Geographical Focus**: The top mission locations reveal areas of persistent conflict or instability. This information can be valuable for understanding global conflict hotspots and allocating resources for future peacekeeping efforts.

4. **Departmental Leadership**: The distribution of missions across lead departments shows which UN bodies are most actively involved in peacekeeping operations. This can provide insights into the types of expertise and resources most frequently required in these missions.

5. **Historical Trends**: The timeline of mission starts offers a historical perspective on UN peacekeeping activities. Peaks in the graph may correspond to periods of increased global conflict or changes in UN peacekeeping policies.

These insights can be valuable for policymakers, researchers, and anyone interested in understanding the scope and nature of UN peacekeeping operations. They highlight the complex, long-term nature of these missions and the global reach of UN peacekeeping efforts.
""")

# Optional: Add interactivity for specific mission details
st.header('7. Individual Mission Details')
selected_mission = st.selectbox('Select a mission for details:', peace_conflict['mission_acronym'].unique())
mission_details = peace_conflict[peace_conflict['mission_acronym'] == selected_mission].iloc[0]
st.write(f"Mission Name: {mission_details['mission_name']}")
st.write(f"Location: {mission_details['mission_location']}")
st.write(f"Start Date: {mission_details['start_date'].date()}")
st.write(f"End Date: {mission_details['end_date'].date() if pd.notnull(mission_details['end_date']) else 'Ongoing'}")
st.write(f"Duration: {mission_details['mission_duration']} days")
st.write(f"Lead Department: {mission_details['lead_department']}")