from altair import Chart, X, Y
import pandas as pd

def create_chart(data):
    if isinstance(data, pd.DataFrame):
        chart = Chart(data).mark_line().encode(
            x=X('index:O', title='Index'),
            y=Y('value:Q', title='Value')
        ).properties(
            title='Scraped Data Visualization'
        )
        return chart
    else:
        raise ValueError("Data must be a pandas DataFrame")