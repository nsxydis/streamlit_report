'''
Purpose: Provide a demonstration of what an interactive report might look like.
'''

# Standard Modules
import streamlit as st
import polars as pl
import altair as alt

# Reporting Module
from streamlit_report import report
r = report.Report()

# Helper file
import helperFile as hf

def main():
    # Read in a data file
    df = pl.read_csv('data.csv', infer_schema_length = None)
    
    # View raw data
    r.ignore = True
    st.write("# This doesn't appear on the final report...")
    r.dataframe(df)
    r.dataframe(df.describe())
    r.ignore = False

    # Sidebar test
    with r.sidebar:
        r.write("Text written to the sidebar or objects placed in the sidebar appear here")

    # Data Description
    r.write("# Data Source")
    link = "https://www.kaggle.com/datasets/fatemehmehrparvar/obesity-levels?resource=download"
    r.write(link)
    r.write("## Data Description")
    block = '''This dataset include data for the estimation of obesity levels in individuals 
from the countries of Mexico, Peru and Colombia, based on their eating habits and physical 
condition. The data contains 17 attributes and 2111 records, the records are labeled with 
the class variable NObesity (Obesity Level), that allows classification of the data using 
the values of Insufficient Weight, Normal Weight, Overweight Level I, Overweight Level II, 
Obesity Type I, Obesity Type II and Obesity Type III. 77% of the data was generated 
synthetically using the Weka tool and the SMOTE filter, 23% of the data was collected 
directly from users through a web platform.'''
    r.write(block)

    # Transform data columns
    df = df.with_columns(
        pl.col('Age') // 5 * 5,
        pl.col('Weight') // 5 * 5,
        pl.col('Height') * 100 // 5 * 5
    )

    # Select breakdown criteria
    number = r.slider("Number of charts", min_value = 1, max_value = 20, step = 1)

    # Note what the tabs do
    r.write("# These tabs can be clicked to display content")
    tab1, tab2, tab3 = r.tabs(['a', 'b', 'c'])
    
    with tab1:
        r.write("You can place text, charts, and other items into a tab group")
    with tab2:
        r.write("Switching tabs hides the content in the other tabs")
    with tab3:
        r.write("Tabs should function in a similar manner as streamlit")

    # Chart tab description
    r.write("# Dynamically created chart tabs based on the dashboard selections")
    r.write("## There is a different chart on each tab")
    r.write("### The charts themselves can be interacted with and display tooltips")

    # Chart tabs
    tabs = list(zip(r.tabs([f"Chart {n + 1}" for n in range(int(number))])))

    cols = df.columns
    for n in range(int(number)):
        with tabs[n][0]:
            mainFeature = r.selectbox("Main feature", key = f'main_{n}', options = cols)
            secondaryFeature = r.selectbox("Secondary feature", key = f'secondary_{n}', options = cols)

            # Make sure we got different features to prevent errors
            if mainFeature == secondaryFeature:
                r.write("You'll need to select different features to generate charts")
                continue
            
            # Create the selection
            selection = alt.selection_point(fields = [mainFeature])
            
            # Minimize the data exposure
            temp = df[[mainFeature, secondaryFeature]]
            data = temp.to_pandas()
            
            # Make the chart
            mainChart = alt.Chart(data).mark_bar().encode(
                x = f'{mainFeature}:N',
                y = 'count()',
                color = alt.condition(selection, f'{mainFeature}:N', alt.value('gray')),
                tooltip = [
                    mainFeature,
                    'count()'
                ]
            ).add_params(selection)

            # Make the secondary chart
            base = alt.Chart(data).mark_bar().encode(
                x = secondaryFeature,
                y = 'count()',
                tooltip = [
                    secondaryFeature,
                    'count()'
                ]
            )
            secondaryChart = alt.layer(
                base.encode(color = alt.value('gray')),
                base.transform_filter(
                    selection
                ).encode(color = f'{mainFeature}:N')
            )

            r.altair_chart(mainChart | secondaryChart)

    # Download Report
    r.download()

if __name__ == '__main__':
    hf.init()
    main()