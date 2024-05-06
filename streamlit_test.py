import streamlit as st
from cassandra.cluster import Cluster

# Connect to Cassandra
@st.cache_resource()
def connect_to_cassandra():
    cluster = Cluster(['127.0.0.1'])  # Change to your Cassandra host
    session = cluster.connect('bigdata')  # Change to your keyspace
    return session

# Function to retrieve data from Cassandra
def get_data_from_cassandra(session):
    query = "SELECT * FROM test"  # Change to your table name
    result_set = session.execute(query)
    return result_set

# Main function
def main():
    # Title and header
    st.title('Cassandra Data Viewer')
    st.header('Viewing data from Cassandra table')

    # Connect to Cassandra
    session = connect_to_cassandra()

    # Retrieve data
    result_set = get_data_from_cassandra(session)

    # Display data in table
    st.subheader('Data from Cassandra:')
    data_rows = []
    for row in result_set:
        data_rows.append(row)
    st.write(data_rows)

# Run the application
if __name__ == '__main__':
    main()
