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
# Type hints & versioning
from __future__ import annotations
from packaging.version import Version
from streamlit.navigation.page import StreamlitPage

# Standard imports
from pathlib import Path
import streamlit as st

# Streamlit imports
from streamlit_report import htmlClass
from contextlib import contextmanager
from streamlit.runtime.scriptrunner import get_script_run_ctx

# If we're using an earlier version of streamlit, the original get_pages method is viable
if Version(st.__version__) < Version("1.44.0"):
    from streamlit.source_util import get_pages

# Otherwise we'll use an alternate method for tracking pages
else:
    get_pages: function = None

class Report:
    def __init__(
            self, 
            duplicatePages: bool = False, 
            pageOrder: list = None,
            styleFile: str = None,
            startActive: bool = False,
        ):
        '''
        duplicatePages: Allow for the program to create multiple pages for 
                        files that have the same name.
        pageOrder:      Order that the pages should appear in, using the names of the page.
        styleFile:      Name of the .html file that specifies the styles to use. If none is 
                        defined, uses the default styles. 
        startActive:    True / False option. If True, reports will default to generating the
                        html code. 
                        NOTE: This only takes effect on the first module to initialize a report.
        '''
        # Session_state shorthand
        self.session_state = st.session_state
        self.ss = self.session_state
        
        # Inititialization
        self.styleFile = styleFile
        self.init('htmlReport', startActive)
        self.init('html', htmlClass.html(self.styleFile))
        self.duplicatePages = duplicatePages

        # Redefine page numbers
        self.init('streamlit_report-htmlRedefinePages', {})
        self.redefine = self.ss['streamlit_report-htmlRedefinePages']
        self.scriptHash = None
        self.nav = False
        
        # If we already have an html report going, preserve it
        self.html: htmlClass.html = self.ss.html

        # Get and store the name of the current page
        try:
            self.html.pageName = self.pageName()
        except:
            # If we're using the navigation options we'll have to keep track of script hashes
            ctx = get_script_run_ctx()
            self.scriptHash = ctx.page_script_hash

            # Check if we've already redefined the hash
            if self.scriptHash in self.redefine:
                self.html.pageName = self.redefine[self.scriptHash]
            else:
                self.html.pageName = self.scriptHash

        # Clear the page data if we're regenerating the code
        self.html.increment(self.duplicatePages)

        # Set the default page order of the report
        self.html.order = pageOrder

        # Option to ignore fields from the report
        self.ignore = False

        # Define the markdown heading level
        self.heading = "###"

        # Define the text to display after a selection field
        self.reportLabel = ' selection:'

        # Define the text to display after a text field
        self.textLabel = ' input:'

        # Optional Function to convert dates
        self.dateFormatFunc = None


    def init(self, variable: str, value: Any) -> None:
        '''Initializes the streamlit session state with the given information'''
        if variable not in self.ss:
            self.ss[variable] = value

    def pageName(self) -> str:
        '''Gets and returns the filename of the running page'''
        # Modified code from blackary in discussion link below...
        # https://discuss.streamlit.io/t/how-can-i-learn-what-page-i-am-looking-at/56980/2
        # NOTE: These modules were removed from st-pages (st_pages)

        # Grab the script run context
        ctx = get_script_run_ctx()

        # NOTE: This code is obsolete in later versions of streamlit
        if Version(st.__version__) < Version('1.44.0'):
            pages = get_pages('')
            hash_string = 'relative_page_hash'
        
        # Otherwise use the page manager to get page names
        else:
            pages = ctx.pages_manager.get_pages()
            hash_string = 'page_script_hash'

        try:
            current_page = pages[ctx.page_script_hash]
        except KeyError:
            current_page = [
                p for p in pages.values() if p[hash_string] == ctx.page_script_hash
            ][0]

        return current_page['page_name']

    def write(self, text: str, **kwargs) -> None:
        '''Mimics st.write'''
        # streamlit
        st.write(text, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(text)

    def markdown(self, text: 'str', **kwargs) -> None:
        '''Mimics st.markdown'''
        # streamlit
        st.markdown(text, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            
            # If we're allowing unsafe html, write to the report directly
            # NOTE: Removed explicit callout for standard streamlit usage
            if 'unsafe_allow_html' in kwargs and kwargs['unsafe_allow_html']:
                self.html.html(text)
            
            # Otherwise, write to the report
            else:
                self.html.write(text)

    def dataframe(
            self, 
            df: DataFrame,      # type: ignore 
            height: str = '400px', 
            width: str = '60%', 
            **kwargs
            ) -> None:
        '''
        Mimics st.dataframe
        NOTE: The height and width variables are no longer used.
        '''
        # streamlit
        st.dataframe(df, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.dataframe(df, height, width)

    def selectbox(self, label: str, options: list, **kwargs) -> str:
        '''Mimics st.selectbox'''
        # streamlit
        selection = st.selectbox(label, options, **kwargs)
        
        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.reportLabel}")
            if selection:
                self.html.write(f"{selection}")
            else:
                self.html.write("Nothing selected")

        # Return the selection
        return selection
    
    def multiselect(
            self, 
            label: str, 
            options: list[str] | DataFrame,  # type: ignore
            **kwargs
            ) -> list:
        '''Mimics st.multiselect'''
        # streamlit 
        values = st.multiselect(label, options = options, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.reportLabel}")
            if len(values) > 0:
                # Write each selection as a comma separated list
                self.html.write(f"{', '.join(str(item) for item in values)}")
            else:
                self.html.write("Nothing selected")

        # Return the selected data
        return values

    def text(self, body: str, **kwargs) -> None:
        '''Mimics st.text'''
        # streamlit
        st.text(body, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f'{body}')
    
    def text_area(self, label: str, **kwargs) -> str:
        '''Mimics st.text_area'''
        # streamlit
        value = st.text_area(label, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f'{self.heading} {label}{self.textLabel}')
            if value:
                self.html.write(f'{value}')
            else:
                self.html.write('No input')

        return value

    def text_input(self, label: str, **kwargs) -> str:
        '''Mimics st.text_input'''
        # streamlit
        value = st.text_input(label, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f'{self.heading} {label}{self.textLabel}')
            if value:
                self.html.write(f'{value}')
            else:
                self.html.write('No input')

        return value

    def slider(self, label: str, **kwargs) -> Any:
        '''Mimics st.slider'''
        # streamlit
        result = st.slider(label, **kwargs)

        # If we're making a report, add to it
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.reportLabel}")
            
            # Check if we have a range of results
            if 'value' in kwargs and type(kwargs['value']) == tuple:
                self.html.write(f"{result[0]} to {result[1]}")

            # Otherwise, display the single result
            else:
                self.html.write(f"{result}")

        # Return the slider output
        return result
    
    def date_input(self, label, **kwargs):
        '''Mimics st.date_input
        dateFormatFunc: Optional function to convert the date into
                        a different format'''
        # streamlit
        value = st.date_input(label, **kwargs)

        # If we're making a report... convert the date
        if self.ss['htmlReport'] and self.ignore == False:
            
            # Process using the given function if provided 
            if self.dateFormatFunc:
                newValue = self.dateFormatFunc(value)

            # Otherwise convert to a string
            else:
                newValue = str(value)

            # Add to the report
            self.html.write(f"{self.heading} {label}{self.reportLabel}")
            self.html.write(f"{newValue}")  

        # Return the st output
        return value  

    def navigation(self, pages, **kwargs) -> StreamlitPage:
        '''Mimics st.navigation'''
        # streamlit
        nav = st.navigation(pages, **kwargs)

        # Shorthand
        redefine = self.ss['streamlit_report-htmlRedefinePages']
        self.nav = True
        
        # Check if we're already redefined this item
        if nav.title not in redefine and self.scriptHash:
            redefine[self.scriptHash] = nav.title

            # For all items to redefine, change the pageNames
            replace = None
            for pageName, pageNumber in self.html.pageNames.items():
                if pageName == self.scriptHash:
                    replace = pageName
                    break

            # Replace the item
            if replace:
                self.html.pageNames[redefine[replace]] = self.html.pageNames.pop(replace)

        return nav

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
        
        # Create the html tab buttons, if we're creating a report
        if self.ss['htmlReport'] and self.ignore == False:
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

    def altair_chart(self, chart: altair.Chart, **kwargs) -> None: # type: ignore
        '''Mimics the altair_chart function of streamlit'''
        # Streamlit
        st.altair_chart(chart, **kwargs)

        # HTML
        if self.ss['htmlReport'] and self.ignore == False:
            self.html.altairChart(chart)

    def download(self, reportName: 'str' = 'output') -> None:
        '''
        Runs the application and downloads the html
            reportName: Name of the report when generated
        '''
        # If the flag is on, create the report
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
    
    def generateReport(self) -> None:
        '''Alternates the report generate value'''
        # If we're not generating a report, clear the saved html code
        if self.ss['htmlReport'] == True:
            self.ss['htmlReport'] = False
            self.ss.html = htmlClass.html(styleFile = self.styleFile)
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