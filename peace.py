import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
from streamlit_folium import folium_static
import folium

# Title and Header
st.title('Peace and Conflict Data')
st.header('Using Python and Streamlit')
st.write('UN Peace and Conflict')

# Load data from URL
data_url = "https://api.psdata.un.org/public/data/DPPADPOSS-PKO/CSV"
peace_conflict = pd.read_csv(data_url)

# Display data types
print(peace_conflict.dtypes)

# Display the DataFrame in Streamlit
st.dataframe(peace_conflict)

# Header and description
st.header("United Nations Peace Missions")
st.write("This is the average mission for UN peace and conflict")

# Selectbox for mission acronym
mission_acronym = st.selectbox(
    label="Select a Mission",
    options=peace_conflict["mission_acronym"].unique().tolist()
)

# Inspect the data
print(peace_conflict['last_update'].head(10))

# Strip whitespace from 'last_update' and convert to datetime
peace_conflict['last_update'] = peace_conflict['last_update'].str.strip()
peace_conflict['last_update'] = pd.to_datetime(peace_conflict['last_update'], errors='coerce')

# Print the first 10 rows of 'last_update'
print(peace_conflict['last_update'].head(10))

# Strip whitespace from 'start_date' and 'end_date' columns
peace_conflict[['start_date', 'end_date']] = peace_conflict[['start_date', 'end_date']].apply(lambda x: x.str.strip())

# Convert 'start_date' and 'end_date' to datetime, with error handling
peace_conflict[['start_date', 'end_date']] = peace_conflict[['start_date', 'end_date']].apply(pd.to_datetime, errors='coerce')

# Print the first 10 rows of 'start_date' and 'end_date'
print(peace_conflict[['start_date', 'end_date']].head(10))

# Identify malformed dates in 'last_update'
malformed_dates = peace_conflict[peace_conflict['last_update'].isna()]['last_update']
print(malformed_dates)

# Print the type of the 10th element in 'last_update'
print(type(peace_conflict['last_update'].iat[10]))

# Find the minimum start date and maximum end date
min_date = peace_conflict['start_date'].min()
max_date = peace_conflict['end_date'].max()
print("Min start date:", min_date)
print("Max end date:", max_date)

# Step 3: Use Streamlit to create an interactive date range selector
date_range = st.date_input(
    label='Select date range',
    value=(min_date.date(), max_date.date()),  # Convert to date objects
    min_value=min_date.date(),
    max_value=max_date.date()
)

# Unpack the date range
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    # Convert selected dates to datetime for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the DataFrame based on the selected date range and mission acronym
    if mission_acronym == 'All':
        filtered_df = peace_conflict[
            ((peace_conflict['start_date'] >= start_date) & (peace_conflict['start_date'] <= end_date)) |
            ((peace_conflict['end_date'] >= start_date) & (peace_conflict['end_date'] <= end_date)) |
            ((peace_conflict['start_date'] <= start_date) & (peace_conflict['end_date'] >= end_date))
        ]
    else:
        filtered_df = peace_conflict[
            (((peace_conflict['start_date'] >= start_date) & (peace_conflict['start_date'] <= end_date)) |
             ((peace_conflict['end_date'] >= start_date) & (peace_conflict['end_date'] <= end_date)) |
             ((peace_conflict['start_date'] <= start_date) & (peace_conflict['end_date'] >= end_date))) &
            (peace_conflict['mission_acronym'] == mission_acronym)
        ]

    # Display the filtered DataFrame in Streamlit
    st.write(filtered_df)

    # Optional: Display some statistics about the filtered data
    st.write(f"Number of missions in selected date range: {len(filtered_df)}")
    if not filtered_df.empty:
        st.write(f"Longest mission duration: {(filtered_df['end_date'] - filtered_df['start_date']).max().days} days")
        st.write(f"Shortest mission duration: {(filtered_df['end_date'] - filtered_df['start_date']).min().days} days")
else:
    st.error("Please select a valid date range.")

# Ensure filtered_df is defined before this point
if 'filtered_df' not in locals():
    st.error("No data available. Please select a valid date range and mission.")
else:
    # Clean and convert numeric columns
    filtered_df.loc[:, 'mission_longitude'] = filtered_df['mission_longitude'].str.replace(',', '').astype(float)
    filtered_df.loc[:, 'mission_latitude'] = filtered_df['mission_latitude'].str.replace(',', '').astype(float)

    # Calculate the average mission_location
    df_avg = filtered_df.groupby(["mission_acronym"], as_index=False).agg({
        "mission_latitude": "first",  # Changed from "Sum" to "first"
        "mission_longitude": "mean"
    })

    # Calculate average location (assuming you want to divide latitude by longitude)
    df_avg["average_location"] = df_avg["mission_latitude"] / df_avg["mission_longitude"]

    # Calculate max average location and add 20%
    max_avg_location = df_avg["average_location"].max()
    max_avg_location = max_avg_location + 0.2 * max_avg_location

    # Rename columns
    df_avg = df_avg.rename(columns={
        "mission_longitude": "Date"
    })

    # Create Altair chart
    chart = alt.Chart(df_avg).mark_line().encode(
        x=alt.X('Date'),
        y=alt.Y(
            'average_location', 
            title='Average Location',
            scale=alt.Scale(zero=True, domain=[0, max_avg_location])
        ),
        tooltip=[
            alt.Tooltip('Date'), 
            alt.Tooltip('average_location', title='Average Location')
        ]
    ).properties(
        title=f"Average Location for {mission_acronym} from {start_date} to {end_date}"
    )

    # Display chart
    st.altair_chart(chart, use_container_width=True)

    # Calculate mission durations
filtered_df['mission_duration'] = (filtered_df['end_date'] - filtered_df['start_date']).dt.days

# Average duration of missions
avg_duration = filtered_df['mission_duration'].mean()
st.write(f"Average mission duration: {avg_duration:.2f} days")

# Longest and shortest missions
longest_mission = filtered_df.loc[filtered_df['mission_duration'].idxmax()]
shortest_mission = filtered_df.loc[filtered_df['mission_duration'].idxmin()]

st.write(f"Longest mission: {longest_mission['mission_acronym']} ({longest_mission['mission_duration']} days)")
st.write(f"Shortest mission: {shortest_mission['mission_acronym']} ({shortest_mission['mission_duration']} days)")

# Distribution of mission durations
fig, ax = plt.subplots()
ax.hist(filtered_df['mission_duration'], bins=20)
ax.set_xlabel('Mission Duration (days)')
ax.set_ylabel('Number of Missions')
ax.set_title('Distribution of Mission Durations')
st.pyplot(fig)