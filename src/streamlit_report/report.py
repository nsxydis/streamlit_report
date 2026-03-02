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
from streamlit.delta_generator import DeltaGenerator

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
            duplicate_pages: bool = False, 
            page_order: list = None,
            style_file: str = None,
            start_active: bool = False,
            **kwargs
        ):
        '''
        duplicate_pages:Allow for the program to create multiple pages for 
                        files that have the same name.
        page_order:     Order that the pages should appear in, using the names of the page.
        style_file:     Name of the .html file that specifies the styles to use. If none is 
                        defined, uses the default styles. 
        start_active:   True / False option. If True, reports will default to generating the
                        html code. 
                        NOTE: This only takes effect on the first module to initialize a report.
        '''
        # Section for backwards compatibility
        style_file = kwargs.get('styleFile', style_file)
        duplicate_pages = kwargs.get('duplicatePages', duplicate_pages)
        page_order = kwargs.get('pageOrder', page_order)
        start_active = kwargs.get('startActive', start_active)

        # Session_state shorthand
        self.session_state = st.session_state
        self.ss = self.session_state
        
        # Inititialization
        self.style_file = style_file
        self.init('html_report', start_active)
        self.init('html', htmlClass.html(self.style_file))
        self.duplicate_pages = duplicate_pages

        # Redefine page numbers
        self.init('streamlit_report-htmlRedefinePages', {})
        self.redefine = self.ss['streamlit_report-htmlRedefinePages']
        self.script_hash = None
        self.nav = False
        
        # If we already have an html report going, preserve it
        self.html: htmlClass.html = self.ss.html

        # Get and store the name of the current page
        try:
            self.html.page_name = self.page_name()
        except:
            # If we're using the navigation options we'll have to keep track of script hashes
            ctx = get_script_run_ctx()
            self.script_hash = ctx.page_script_hash

            # Check if we've already redefined the hash
            if self.script_hash in self.redefine:
                self.html.page_name = self.redefine[self.script_hash]
            else:
                self.html.page_name = self.script_hash

        # Clear the page data if we're regenerating the code
        self.html.increment(self.duplicate_pages)

        # Set the default page order of the report
        self.html.order = page_order

        # Option to ignore fields from the report
        self.ignore = False

        # Define the markdown heading level
        self.heading = "###"

        # Define the text to display after a selection field
        self.report_label = ' selection:'

        # Define the text to display after a text field
        self.textLabel = ' input:'

        # Optional Function to convert dates
        self.date_format_func = None


    def init(self, variable: str, value: Any) -> None:
        '''Initializes the streamlit session state with the given information'''
        if variable not in self.ss:
            self.ss[variable] = value

    def page_name(self) -> str:
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
        if self.ss['html_report'] and self.ignore == False:
            self.html.write(text)

    def markdown(self, text: 'str', **kwargs) -> None:
        '''Mimics st.markdown'''
        # streamlit
        st.markdown(text, **kwargs)

        # If we're making a report, add to it
        if self.ss['html_report'] and self.ignore == False:
            
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
        if self.ss['html_report'] and self.ignore == False:
            self.html.dataframe(df, height, width)

    def selectbox(self, label: str, options: list, **kwargs) -> str:
        '''Mimics st.selectbox'''
        # streamlit
        selection = st.selectbox(label, options, **kwargs)
        
        # If we're making a report, add to it
        if self.ss['html_report'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.report_label}")
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
        if self.ss['html_report'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.report_label}")
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
        if self.ss['html_report'] and self.ignore == False:
            self.html.write(f'{body}')
    
    def text_area(self, label: str, **kwargs) -> str:
        '''Mimics st.text_area'''
        # streamlit
        value = st.text_area(label, **kwargs)

        # If we're making a report, add to it
        if self.ss['html_report'] and self.ignore == False:
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
        if self.ss['html_report'] and self.ignore == False:
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
        if self.ss['html_report'] and self.ignore == False:
            self.html.write(f"{self.heading} {label}{self.report_label}")
            
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
        date_format_func: Optional function to convert the date into
                        a different format'''
        # streamlit
        value = st.date_input(label, **kwargs)

        # If we're making a report... convert the date
        if self.ss['html_report'] and self.ignore == False:
            
            # Process using the given function if provided 
            if self.date_format_func:
                new_value = self.date_format_func(value)

            # Otherwise convert to a string
            else:
                new_value = str(value)

            # Add to the report
            self.html.write(f"{self.heading} {label}{self.report_label}")
            self.html.write(f"{new_value}")  

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
        if nav.title not in redefine and self.script_hash:
            redefine[self.script_hash] = nav.title

            # For all items to redefine, change the page_names
            replace = None
            for page_name, page_number in self.html.page_names.items():
                if page_name == self.script_hash:
                    replace = page_name
                    break

            # Replace the item
            if replace:
                self.html.page_names[redefine[replace]] = self.html.page_names.pop(replace)

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
    
    def tabs(self, items: 'list', display_index: 'int' = 0, **kwargs):
        '''Mimics the functionality of st.tabs
        NOTE: For the html report it will default to setting the first tab active'''
        # Get the current tab count
        n = self.html.tab_count + 1
        
        # Create the html tab buttons, if we're creating a report
        if self.ss['html_report'] and self.ignore == False:
            self.html.tab_bar(items)

        # streamlit
        # Create the tabs
        streamlit_tabs = zip(st.tabs(items, **kwargs))
        tabs_list = []

        # Create the tab group name
        group = f"group_{self.html.tab_group}_tablink"
        
        # Unzip the items and write to each of them
        i = 0
        for item in streamlit_tabs:
            # Append to our tabs
            id = f"page_{self.html.page}_{items[i]}_{n}"

            # If i == display_index then we want to show the tab
            if i == display_index:
                display = ''
            # Otherwise, hide the tab
            else:
                display = 'style = "display:none"'

            # Add and create the tab
            tabs_list.append(tab(item[0], self, id, group, display))

            # Increment i & n so we can keep track of the tab index
            i += 1
            n += 1

        # Yield function
        for t in tabs_list:
            yield t.combo

    def altair_chart(self, chart: altair.Chart, **kwargs) -> DeltaGenerator: # type: ignore
        '''Mimics the altair_chart function of streamlit'''
        # Streamlit
        delta_gen = st.altair_chart(chart, **kwargs)

        # HTML
        if self.ss['html_report'] and self.ignore == False:
            self.html.altair_chart(chart)

        # Return the delta generator
        return delta_gen

    def download(self, report_name: 'str' = 'output') -> None:
        '''
        Runs the application and downloads the html
            report_name: Name of the report when generated
        '''
        # If the flag is on, create the report
        if self.ss['html_report'] == True:
            # Make the report...
            self.html.generate_report()

            # Download button
            st.download_button("Download!", self.html.report, f'{report_name}.html')
            helpText = "Stopping report generation can improve application speeds"
            st.button('Stop Report Generation', on_click = self.generate_report, help = helpText)
        else:
            # Otherwise ask to download
            st.button('Generate Report?', on_click = self.generate_report)
    
    def generate_report(self) -> None:
        '''Alternates the report generate value'''
        # If we're not generating a report, clear the saved html code
        if self.ss['html_report'] == True:
            self.ss['html_report'] = False
            self.ss.html = htmlClass.html(style_file = self.style_file)
        else:
            self.ss['html_report'] = True

    def plotly_chart(
            self, 
            chart, 
            override_streamlit_colors: bool = True,
            **kwargs
            ) -> DeltaGenerator:
        '''
        Plot a plotly chart
            chart:  Plotly chart
            override_streamlit_colors:  True/False -- If true, will override the default streamlit color scheme.
                                        NOTE: This is required because streamlit will override plotly colors and
                                        result in a black/white html output if not overridden.
                                        NOTE: This may result in the colors displaying on streamlit to change
                                        once report generation is triggered.
        '''
        # Update the html class that we have plotly charts
        self.html.has_plotly_charts = True

        # If we're overriding streamlit's color scheme, do so here
        if override_streamlit_colors:
            import plotly.io as pio
            pio.templates.default = 'plotly'
        
        # Show the plotly chart
        chart_state = st.plotly_chart(chart, **kwargs)

        # If we embedding the chart...
        if self.ss['html_report'] == True:
            # Import the chart extractor
            from streamlit_report import plotly_extractor
            
            # Write the chart to the html body
            self.ss.html.html(
                plotly_extractor.get_body_html(chart)
            )

        # Return the streamlit chart state
        return chart_state

class tab:
    def __init__(self, st_tab, report, id, group, display):
        self.st_tab = st_tab
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
        if self.report.ss['html_report'] and self.report.ignore == False:
            self.html.html(code)

        # Activate the tab block
        self.html.tab_id = self.id

        # Yield for streamlit
        yield self.st_tab

        # Close the div block (if we're not ignoring)
        if self.report.ss['html_report'] and self.report.ignore == False:
            self.html.html('</div>')

    @property
    @contextmanager
    def combo(self):
        with self.tab, self.st_tab:
            yield