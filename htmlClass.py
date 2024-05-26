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
        self.pageNames = {}         # Names of each page associated with a page number
        self.pageOrder = []         # Order that the pages should be displayed in
        
        self.charts = 0             # Chart counter
        self.altairCharts = False   # Chart boolean
        self.side = False           # If true, writes to the sidebar
        self.lineBreak = True       # If true, puts a break between certain elements (charts, dataframes...)

        # Tab and page counts
        self.page = 1               # The current page number
        self.pageName = ''          # Name of the current page
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

    def increment(self, allowDuplicates : 'bool' = False):
        '''Increments the page or goes to the given page and clears its content'''
        # If we're allowing duplicates or have a new page...
        if allowDuplicates == True or self.pageName not in self.pageNames:
            self.page = len(self.pageNames) + 1
            self.pageNames[self.pageName] = self.page
        
        # Otherwise, the tab already exists and needs to be overwritten
        elif allowDuplicates == False:
            # Navigate to this page
            self.page = self.pageNames[self.pageName]
        
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

        // Set the width of the side navigation to 250px and the left margin of the page content to 250px
        var k, contentPages, sidebarContent;

        // Get all the pages with content & sidebar content on them
        contentPages = document.getElementsByClassName("content");
        sidebarContent = document.getElementsByClassName("sidebar");

        function openNav() {
        // Open the Navigation window
        document.getElementById("pageNav").style.width = "250px";
        
        // Open the sidebars
        for (k = 0; k < sidebarContent.length; k ++) {
            sidebarContent[k].style.width = "250px";
        }

        // Adjust the margin for all the content pages
        for (k = 0; k < contentPages.length; k ++) {
            contentPages[k].style.marginLeft = "250px";    
            }
        }

        // Set the width of the side navigation to 0 and the left margin of the page content to 0
        function closeNav() {
        // Close the Page Navigation bar
        document.getElementById("pageNav").style.width = "0";

        // Close the sidebars
        for (k = 0; k < sidebarContent.length; k ++) {
            sidebarContent[k].style.width = "0";
            sidebarContent[k].style.marginLeft = "0";
        }


        // Move all the content windows over
        for (k = 0; k < contentPages.length; k ++) {
            contentPages[k].style.marginLeft = "0";    
            }
        } 

        // Functions to switch between pages
        function openPage (evt, page_id) {
        // Clear the content display for all pages
        for (k = 0; k < contentPages.length; k ++) {
            contentPages[k].style.display = "none";
        }

        // Clear the sidebar content display for all pages
        for (k = 0; k < sidebarContent.length; k ++) {
            sidebarContent[k].style.display = "none";
        }

        // Display the page that was clicked on
        document.getElementById(page_id).style.display = "block";
        document.getElementById(page_id + "_sidebar").style.display = "block";

        }

        </script>
        '''
        return code

    def tabBar(self, items: 'list'):
        '''Creates a tab bar with buttons for each item in the list'''
        # Open the div element
        self.html(f'<div class = "tab">\n')

        # Increment the tab group
        self.tabGroup += 1
        
        # Add each of the tabs
        for item in items:
            self.tabCount += 1
            code = f'''
            <button class = "page_{self.page}_group_{self.tabGroup}_tablink" 
            onclick = "openTab( event, {self.page}, {self.tabGroup}, 
                                'page_{self.page}_{item}_{self.tabCount}')">
                {item}
            </button>
            '''
            self.html(code)

        # Close the element
        self.html('</div>\n')

    def pageTabs(self, order: 'list' = None):
        '''Adds the pages to the sidebar in the order generated or in an order specified
        NOTE: The order is a list of the page names, not the page numbers as those can change
        NOTE: This code is similar but functionally different to the tabBar function'''
        # Initialize
        code = ''

        # Increment the tab group
        self.tabGroup += 1

        # Determine the order to create the tabs
        self.pageOrder = []

        # Start with the provided order
        if order:
            for item in order:
                # Only add the item to our page tabs if it exists in our data
                if item in self.pageNames:
                    self.pageOrder.append(item)

        # Add any remaining tabs in the order they were generated
        for item in self.pageNames:
            if item not in self.pageOrder:
                self.pageOrder.append(item)

        # Add a tab for each page
        for item in self.pageOrder:
            self.tabCount += 1
            code += f'''
            <a href = "#{item}" class = "page_link" 
            onclick = 'openPage( event, "{item}_{self.pageNames[item]}")'>
                {item}
            </a>
            '''

        # Close the element
        # code += '</div>\n'
        return code
            
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

    def pName(self, number):
        '''For the given page number, returns the page name'''
        # Default value is None
        n = None
        
        # Loop through all the pages we collected data for
        for name in self.pageNames:
            if number == self.pageNames[name]:
                n = name
                break

        # Return the page name
        return n

    def generateReport(self, order = None):
        # Create the main body block
        self.main = '''<body onload = "openNav()">
        <div id = "pageNav" class = "sidenav">
        <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
        '''

        # If we have multiple pages, add their buttons to the sidebar
        if len(self.pageNames) > 1:
            self.main += self.pageTabs(order)

        # NOTE: Sidebar now is grouped with sidenav by default
        for item in self.sidebar:
            # Get the name of the page if we have multiple pages
            name = self.pName(item)
            barID = f'id = "{name}_{item}_sidebar"' if name else ''

            display = ''
            if len(self.pageOrder) > 0:
                if name == self.pageOrder[0]:
                    display += 'style = "display: block"'
                else:
                    display += 'style = "display: none"'
            else:
                display = ''

            # Add each item to the sidenav
            self.main += f'<div class = "sidebar" {barID} {display}>\n'

            self.main += self.sidebar[item] + '\n'
            self.main += '</div>'

        # Close the sidenav block
        self.main += '</div>\n'

        for item in self.body:
            # Get the name of the page if we have multiple pages
            name = self.pName(item)
            id = f'id = "{name}_{item}"' if name else ''

            display = 'style = "margin-left: 0;'
            if len(self.pageOrder) > 0:
                if name == self.pageOrder[0]:
                    display += 'display: block"'
                else:
                    display += 'display: none"'
            else:
                display = ''
            
            self.main += f'''
            <div class = "content" {id} {display}> 
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