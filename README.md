# Purpose
This module creates a streamlit page using standard streamlit commands and, when prompted, generates an html report that mirrors the dashboard's interactive contents. The final report stores the results that are displayed on the page and lives on as a static file that can be viewed without connecting to the dashboard.

Styles can be modified by changing the styles.html file. Current styles were based off references found on https://www.w3schools.com/.

# Note
The below features are simplified representations of what the dashboard presents. Streamlit has features that are not and may never be implemented by this library. The purpose is to streamline a simple and static reporting mechanism without having to write additional code. 

# Current and Planned Features
- [x] _streamlit.write_ support for markdown and basic text
- [ ] _streamlit.write_ support for list, dictionary types
- [x] _streamlit.tabs_ support using **with** generator functions
- [x] _streamlit.sidebar_ support using **with** generator functions
- [ ] _streamlit.cols_ support using **with** generator functions
- [ ] multi-page app support
- [x] _streamlit.altair_chart_ support
- [x] _streamlit_report.Report.ignore_ flag to temporarily suppress writing to the report file
- [x] _streamlit.dataframe_ support, displaying a polars or pandas dataframe in a sized window
- [x] _streamlit.selectbox_ support, displaying the name of the item selected during report generation
- [ ] _streamlit.multiselectbox_ support, displaying the name of the items selected during report generation
- [x] _streamlit.slider_ support for single value slider selections
- [ ] _streamlit.slider_ support for multipoint values selections
- [x] report generation and download button for single page reports
- [ ] improved style defaults