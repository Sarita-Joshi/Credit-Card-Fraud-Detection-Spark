import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
from cassandra.cluster import Cluster

# Global variable to store the last processed row's timestamp
last_timestamp = None

# Connect to Cassandra
@st.cache_resource()
def connect_to_cassandra():
    cluster = Cluster(['127.0.0.1'])  # Change to your Cassandra host
    session = cluster.connect('bigdata')  # Change to your keyspace
    return session

# Function to retrieve recent new rows from Cassandra
def get_recent_data_from_cassandra(session):
    global last_timestamp
    # Construct query to select rows newer than the last processed row
    if last_timestamp:
        query = f"SELECT * FROM bank WHERE ts > '{last_timestamp}' ALLOW FILTERING"
    else:
        query = "SELECT * FROM bank"  # Select all rows if it's the first iteration
        
    result_set = session.execute(query)
    df = pd.DataFrame(list(result_set))
    
    # Update last_timestamp with the timestamp of the newest row
    if not df.empty:
        last_timestamp = int(df['ts'].max().timestamp() * 1000)
        print(last_timestamp, type(last_timestamp))
    return df

# Main function
def main():
    st.set_page_config(
        page_title='Real-Time Data Science Dashboard',
        page_icon='✅',
        layout='wide'
    )

    # dashboard title
    st.title("Real-Time / Live Data Science Dashboard")

    session = connect_to_cassandra()
    df = get_recent_data_from_cassandra(session)
    print(df.columns)
        
    # top-level filters
    job_filter = st.selectbox("Select the Job", ['All Jobs'] + list(pd.unique(df['job'])))

    # creating a single-element container
    placeholder = st.empty()

    # near real-time / live feed simulation
    while True:
        df_recent = get_recent_data_from_cassandra(session)
        df = pd.concat([df,df_recent], ignore_index=True)

        print(df.columns)
        df['age_new'] = df['age'] * np.random.choice(range(1,5))
        df['balance_new'] = df['balance'] * np.random.choice(range(1,5))

        if job_filter!='All Jobs':
            df = df[df['job'] == job_filter]

        with placeholder.container():
            # create three columns for KPIs
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)

            # fill in those three columns with respective metrics or KPIs
            avg_age = np.mean(df['age_new'])
            count_married = int(df[df["marital"] == 'married']['marital'].count() + np.random.choice(range(1, 30)))
            balance = np.mean(df['balance_new'])

            kpi1.metric(label="Age ⏳", value=round(avg_age), delta=round(avg_age) - 10)
            kpi2.metric(label="Married Count 💍", value=int(count_married), delta=-10 + count_married)
            kpi3.metric(label="A/C Balance ＄", value=f"$ {round(balance, 2)} ",
                        delta=-round(balance / count_married) * 100)
            kpi4.metric(label="Total", value=round(df.shape[0]), delta=round(df.shape[0]) - 10)
                        

            # create two columns for charts
            fig_col1, fig_col2 = st.columns(2)

            # plot the first chart
            with fig_col1:
                st.markdown("### First Chart")
                fig = px.density_heatmap(data_frame=df, y='age_new', x='marital')
                st.write(fig)

            # plot the second chart
            with fig_col2:
                st.markdown("### Second Chart")
                fig2 = px.histogram(data_frame=df, x='age_new')
                st.write(fig2)

            # Display detailed data view
            st.markdown("### Detailed Data View")
            st.dataframe(df)

            time.sleep(5)

if __name__ == "__main__":
    main()
