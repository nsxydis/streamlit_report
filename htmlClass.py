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

Purpose: HTML class for use in generating reports.
'''

import markdown
import polars as pl

class html:
    def __init__(self):
        # Note this code is static for all pages
        self.head = self.header()
        self.script = self.tabCode()
        self.report = None          # This will contain the code of the full report

        # Note these fields will be unique to each page
        self.body = {}              # Dictionary of body code for each page
        self.sidebar = {}           # Dictionary for sidebar code
        self.chartScript = {}       # Dictionary for chart scripts
        
        self.charts = 0             # Chart counter
        self.altairCharts = False   # Chart boolean
        self.side = False           # If true, writes to the sidebar
        self.lineBreak = True       # If true, puts a break between certain elements (charts, dataframes...)

        # Tab and 
        self.page = 1               # The current page number
        self.tabCount = 0           # Current tab count
        self.tabGroup = 0           # Current tab group

        # Init the body and sidebar sections
        self.clear()

    def clear(self):
        '''Clears page code, including if the current page has been generated before'''
        pageContent = [
            self.body,
            self.sidebar,
            self.chartScript
        ]

        # Loop through each of the pages with content
        for item in pageContent:
            item[self.page] = ''

        # Reset trigger variables
        self.altairCharts = False

    def increment(self, page: 'int' = None):
        '''Increments the page or goes to the given page and clears its content'''
        # Navigate to the target page
        if page:
            self.page = page
        else:
            self.page += 1

        # Clear and/or initialize the page
        self.clear()

    def header(self):
        '''Default header code'''
        # Starting code
        head = '''
        <!DOCTYPE html>
        <html>
        <head>
        '''
        
        # Read in the style html and add to our head code
        text = ''
        with open('style.html') as f:
            for line in f.readlines():
                text += line
        head += text

        return head

    def tabCode(self):
        '''Writes the tab javascript code for tab navigation'''
        code = '''
        <script>
        // For a specific tab group, close all the other tabs and open one of interest
        function openTab(evt, page, group, tabName) {
        var i, x, tablinks;

        // Clear previous tab contents
        x = document.getElementsByClassName("group_" + group + "_tablink");
        for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
        }

        // Set the active tab highlight
        tablinks = document.getElementsByClassName("page_" + page + "_group_" + group + "_tablink");
        for (i = 0; i < x.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
        }
        </script>
        '''
        return code

    def tabBar(self, items: 'list', vTab = False):
        '''Creates a tab bar with buttons for each item in the list'''
        # Add a v if we're making a vertical tab (multipage app)
        if vTab:
            v = 'v'

            # Keep track of whether or not to disable the sidebar
            if self.sidebar:
                disable = False
            else:
                self.sidebar = True
                disable = True
        
        # If we're not making a vertical tab, then v is blank
        else:
            v = ''

        # Open the div element
        self.body[self.page] += f'<div class = "{v}tab">\n'

        # Increment the tab group
        self.tabGroup += 1
        
        # Add each of the tabs
        for item in items:
            self.tabCount += 1
            self.body[self.page] += f'''
            <button class = "page_{self.page}_group_{self.tabGroup}_tablink" 
            onclick = "openTab(event, {self.page}, {self.tabGroup}, 'page_{self.page}_{item}_{self.tabCount}')">{item}</button>'''

        # Close the element
        self.body[self.page] += '</div>'

        # If we need to, disable the sidebar
        if disable:
            self.sidebar = False


    def altairHeader(self):
        '''Optional code to add to the header if we're using altair charts'''
        import altair as alt

        altairChartStyle = '''
            <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
            <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
            <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
        </head>'''

        # Update the chart information
        altairChartStyle = altairChartStyle.format(
            vega_version=alt.VEGA_VERSION,
            vegalite_version=alt.VEGALITE_VERSION,
            vegaembed_version=alt.VEGAEMBED_VERSION
        )

        # Return the code
        return altairChartStyle
    
    def write(self, text):
        '''HTML for the write command'''
        # Generate the markdown code
        code = markdown.markdown(text)
        
        # Write the code
        self.html(code)

    def altairChart(self, chart):
        '''HTML to display an altair chart'''
        # Increment our global count by one
        self.charts += 1
        chartNumber = self.charts

        # Chart code
        chartCode = f'''<div id="vis{chartNumber}"></div>\n'''

        # If lineBreak, then add a <br> to the chart code
        if self.lineBreak:
            chartCode += " \n <br> \n"

        # Write the chart code
        self.html(chartCode)

        # If we're running for the first time, add the script code
        if self.altairCharts == False:
            self.chartScript[self.page] += '''<script type="text/javascript">\n'''
            self.altairCharts = True
        
        # Append to the chart script
        self.chartScript[self.page] += f'''vegaEmbed('#vis{chartNumber}', {chart.to_json(indent = None)}).catch(console.error);\n'''

    def html(self, code):
        '''Adds the code to the body or sidebar'''
        # Write to the sidebar
        if self.side:
            self.sidebar[self.page] += code
        
        # Write to the main body
        else:
            self.body[self.page] += code

    def dataframe(self, df, height = '400px', width = '60%'):
        '''Writes the html code needed for a dataframe'''
        # If we have a polars dataframe, convert to pandas
        if type(df) == pl.DataFrame:
            df = df.to_pandas()

        # Create the html code for the table
        table = df.to_html(index = False)

        # Create an iframe around the table
        code = f'''<div style = "overflow:auto; height:{height}; width:{width}">
        {table}
        </div>
        '''

        # Line break
        if self.lineBreak:
            code += "<br>"

        # Write the code
        self.html(code)

    def generateReport(self):
        # Create the main body block
        self.main = '<body>'

        # TODO: Make the sidebar code work for multipage apps
        # NOTE: For now just force everything onto the same sidebar
        self.main += '<div class = "sidebar">\n'
        for item in self.sidebar:
            self.main += self.sidebar[item] + '\n'
        self.main += '</div>'

        # TODO: Make the body code work for multipage apps
        for item in self.body:
            self.main += f'''
            <div class = "content"> 
                {self.body[item]}
            </div>'''
        
        # Add the chartScript if there is some
        first = True
        altairHead = ''
        for item in self.chartScript:
            # Check that there's altair code to add
            if self.chartScript[item] != '':
                # If it's the first time, add to our altair header
                if first:
                    altairHead = self.altairHeader()
                    first = False
                
                # Add the altair script code
                self.main += f'''
                    {self.chartScript[item]}
                </script>'''
        
        # Close the code block
        self.head += altairHead + '\n</head>'
        self.main += "</body>\n"
        self.report = self.head + self.main + self.script + '</html>'

        # Return the report
        return self.report