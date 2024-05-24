'''
   Copyright 2024 Nick Xydis

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Purpose: Streamline creation of html reports when creating a streamlit dashboard.

Author: Nick Xydis
'''

import streamlit as st
import htmlClass
from contextlib import contextmanager

class Report:
    def __init__(self):
        # Session_state shorthand
        self.session_state = st.session_state
        self.ss = self.session_state
        
        # Inititialization
        self.init('htmlReport', False)
        self.init('html', htmlClass.html())

        # If we already have an html report going, preserve it
        self.html = self.ss.html

        # Clear the page data if we're regenerating though
        self.html.clear()

        # Option to ignore fields from the report
        self.ignore = False

        # Define the markdown heading level
        self.heading = "###"

        # Define the lable to display after a selection field
        self.reportLabel = ' selection'

    def init(self, variable, value):
        '''Initializes the session state with the given information'''
        if variable not in self.ss:
            self.ss[variable] = value

    def write(self, text, **kwargs):
        '''Mimics st.write'''
        # streamlit
        st.write(text, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(text)

    def dataframe(self, df, height = '400px', width = '60%', **kwargs):
        '''Mimics st.dataframe'''
        # streamlit
        st.dataframe(df, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.dataframe(df, height, width)

    def selectbox(self, label, options, **kwargs):
        '''Mimics st.selectbox'''
        # streamlit
        selection = st.selectbox(label, options, **kwargs)
        
        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.reportLabel}:")
            self.html.write(f"{selection}")

        # Return the selection
        return selection
    
    def slider(self, label, **kwargs):
        '''Mimics st.slider'''
        # streamlit
        value = st.slider(label, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f"{self.heading} {value}{self.reportLabel}")
            self.html.write(f"{value}")

    @property
    @contextmanager 
    def sidebar(self):
        '''Adds items to the sidebar'''
        # Note that we have a sidebar
        self.html.side = True
        with st.sidebar:
            yield
        self.html.side = False
    
    def tabs(self, items: 'list', displayIndex: 'int' = 0, **kwargs):
        '''Mimics the functionality of st.tabs
        NOTE: For the html report it will default to setting the first tab active'''
        # Get the current tab count
        n = self.html.tabCount + 1
        
        # Create the html tab buttons
        self.html.tabBar(items)

        # streamlit
        # Create the tabs
        streamlitTabs = zip(st.tabs(items, **kwargs))
        tabsList = []

        # Create the tab group name
        group = f"group_{self.html.tabGroup}_tablink"
        
        # Unzip the items and write to each of them
        i = 0
        for item in streamlitTabs:
            # Append to our tabs
            id = f"page_{self.html.page}_{items[i]}_{n}"

            # If i == displayIndex then we want to show the tab
            if i == displayIndex:
                display = ''
            # Otherwise, hide the tab
            else:
                display = 'style = "display:none"'

            # Add and create the tab
            tabsList.append(tab(item[0], self, id, group, display))

            # Increment i & n so we can keep track of the tab index
            i += 1
            n += 1

        # Yield function
        for t in tabsList:
            yield t.combo

    def altair_chart(self, chart):
        '''Mimics the altair_chart function of streamlit'''
        # Streamlit
        st.altair_chart(chart)

        # HTML
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.altairChart(chart)

    def download(self, reportName = 'output'):
        '''Runs the application and downloads the html'''
        if self.ss['htmlReport'] == True:
            # Make the report...
            self.html.generateReport()

            # Download button
            st.download_button("Download!", self.html.report, f'{reportName}.html')
            helpText = "Stopping report generation can improve application speeds"
            st.button('Stop Report Generation', on_click = self.generateReport, help = helpText)
        else:
            # Otherwise ask to download
            st.button('Generate Report?', on_click = self.generateReport)
    
    def generateReport(self):
        '''Alternates the report generate value'''
        # If we're not generating a report, clear the saved html code
        if self.ss['htmlReport'] == True:
            self.ss['htmlReport'] = False
            self.ss.html = htmlClass.html()
        else:
            self.ss['htmlReport'] = True

class tab:
    def __init__(self, stTab, report, id, group, display):
        self.stTab = stTab
        self.report = report
        self.html = report.html
        self.id = id
        self.group = group
        self.display = display

    @property
    @contextmanager
    def tab(self):
        # HTML Stuff
        code = f'''<div id = "{self.id}" class = "{self.group}" {self.display}>'''

        # Only write the code if we're not ignoreing right now
        if self.report.ss['htmlReport'] and self.report.ignore == False:
            self.html.html(code)

        # Activate the tab block
        self.html.tabID = self.id

        # Yield for streamlit
        yield self.stTab

        # Close the div block (if we're not ignoring)
        if self.report.ss['htmlReport'] and self.report.ignore == False:
            self.html.html('</div>')

    @property
    @contextmanager
    def combo(self):
        with self.tab, self.stTab:
            yield

# Application testing...
def main():
    r = report()
    r.write('# Hello World')
    r.write("# This is a test")

    with r.sidebar:
        options = ['a', 'b', 'c', 'd', 'e']
        r.selectbox("These are some options", options = options, index = 2)
    
    # Sidebar testing...
    with r.sidebar:
        r.write("Hello world")

    # Chart testing
    import altair as alt
    import polars as pl
    df = pl.DataFrame(
        {
            'x' : [n for n in range(1000)],
            'y' : [n**2 for n in range(1000)]
        }
    )
    chart = alt.Chart(df.to_pandas()).mark_line().encode(
        x = 'x', y = 'y'
    )
    r.altair_chart(chart)
    r.altair_chart(chart)
    r.altair_chart(chart)

    # Download
    r.download()

if __name__ == '__main__':
    main()
