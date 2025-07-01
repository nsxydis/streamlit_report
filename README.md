# How to use
1. Install the package into your environment:
```bash
pip install streamlit-report
```
2. Call the report class in your program:
```python
from streamlit_report import report
r = report.Report()
```
3. For supported functions, replace _st._ with _r._ and the Report class will call the streamlit function and write to your report simultaneously.
4. Call the download method to add a button to toggle report generation and download: 
```python
r.download()
```
5. Run your dashboard, click the **Generate Report?** button, navigate to each page, activate the content you'd like to add to your report, and click the **Download!** button when done. NOTE: the report overwrites a page's content each time you visit it on the dashboard.

# Purpose
This module creates a streamlit page using standard streamlit commands and, when prompted, generates an html report that mirrors the dashboard's interactive contents. The final report stores the results that are displayed on the page and lives on as a static file that can be viewed without connecting to the dashboard.

Styles can be modified by changing the styles.html file. Current styles were based off references found on https://www.w3schools.com/.
 
# Note
The below features are simplified representations of what the dashboard presents. Streamlit has features that are not and may never be implemented by this library. The purpose is to streamline a simple and static reporting mechanism without having to write additional code. 

# Version History

## Version 0.0.7
- updated default style.html file to improve dataframe display on reports
- removed height & width functionality from r.dataframe commands
    * This can now be specified globally in the dataframe-container & dataframe CSS
- removed dependency version requirements on imported modules

## Version 0.0.6
- updated support to account for migrated get_pages function in streamlit Version 1.44
- fixed bug in multiselect code
- added support for navigation based multipage applications
- added some minor QoL updates via type hints

## Version 0.0.4-alpha
- added st.date_input support
- added st.multiselect support
- added st.text, st.text_area, st.text_input support
- added st.slider support for range value selections

## Version 0.0.3
- Restructured repository layout 
- Reformatted the README.md file
- Removed demo and related programs from the main branch
    * They still exist on the demo branch and are primarily used for the streamlit cloud demo page

## Version 0.0.2
- added functions removed from st_pages to restore page name detection
- moved demo program and data to the examples folder

## Version 0.0.1
Added basic functionality including multipage support, altair graphs, and some input data fields.
- _streamlit.write_ support for markdown and basic text
- _streamlit.markdown_ support -- **allow_unsafe_html = True** will write custom html code to the report
- _streamlit.tabs_ support using **with** generator functions
- _streamlit.sidebar_ support using **with** generator functions
- collapsable sidebar
- _streamlit.altair_chart_ support
- _streamlit_report.Report.ignore_ flag to temporarily suppress writing to the report file
- _streamlit.dataframe_ support, displaying a polars or pandas dataframe in a sized window
- _streamlit.selectbox_ support, displaying the name of the item selected during report generation
- _streamlit.slider_ support for single value slider selections
- report generation and download button for single page reports
- multi-page app support
- creation of single report for multi-page applications
- option to specify the default page order that a report generates in

# Planned Features
## Priority items
+ [x] Create distribution file
+ [x] st.date_input
+ [x] st.multiselect
+ [x] st.text_input
+ [x] st.text_area

## Lower priority items
+ [ ] st.columns
+ [x] st.text
+ [ ] button to reveal the collapsed sidebar
+ [x] _streamlit.slider_ support for multipoint values selections 
+ [ ] improved style defaults
+ [ ] option to write to temporary files instead of storing the html code in memory

## Needs review
+ [ ] st.form
+ [ ] st.image
+ [ ] st.logo
+ [ ] st.page_link
+ [x] st.navigation
+ [ ] resizable sidebar
+ [ ] _streamlit.write_ support for list, dictionary types
+ [ ] option to only replace page content when a button is pressed

## Unsupported Features
- pdf report option