'''
Purpose: This is for testing multi-page app support.
'''
# Standard Modules
import streamlit as st
import polars as pl
import altair as alt

# Custom Reporting Module
import report
r = report.Report()

def main():
    # Display the page name
    import sys
    st.write(__file__)
    st.write(sys.argv[0])
    

    # Ask for a number of points to plot
    points = r.slider('Number of points to plot on the curve', min_value = 100, max_value = 2000)
    
    # Make some basic data in a dataframe
    df = pl.DataFrame({
        'x' : [n for n in range(points)],
        'y' : [n**2 for n in range(points)]
    })

    # Minor heading
    r.write('# This is an exponential curve based on the number of points asked for')

    # Display the data
    r.dataframe(df)

    # Make a chart
    chart = alt.Chart(df.to_pandas()).mark_line().encode(
        x = 'x',
        y = 'y',
        tooltip = ['x', 'y']
    )
    r.altair_chart(chart)

    # Download Report
    r.download()

    # TEMP TESTING
    st.write(r.html.pageNames)

if __name__ == '__main__':
    main()