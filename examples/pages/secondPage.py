'''
Purpose: This is for testing multi-page app support.
'''
# Standard Modules
import streamlit as st
import polars as pl
import altair as alt
import random

# Custom Reporting Module
import report
r = report.Report()

# Helper File
import helperFile as hf

def main():
    # Ask for a number of points to plot
    points = r.slider('Number of points to plot on the curve', min_value = 100, max_value = 2000)
    
    # Make some basic data in a dataframe
    df = pl.DataFrame({
        'x' : [n for n in range(points)],
        'y' : [n**2 + random.randint(-n*10, n*10) for n in range(points)]
    })

    # Minor heading
    r.write('# This is an exponential curve based on the number of points asked for')
    r.write("## Some random fluctuations were added")

    # Display the data
    display = st.checkbox('Display dataframe on report')
    if not display:
        r.ignore = True
    r.dataframe(df)
    r.ignore = False

    # Make a chart
    chart = alt.Chart(df.to_pandas()).mark_line().encode(
        x = 'x',
        y = 'y',
        tooltip = ['x', 'y']
    )
    r.altair_chart(chart)

    # Download Report
    r.download()

if __name__ == '__main__':
    hf.init()
    main()