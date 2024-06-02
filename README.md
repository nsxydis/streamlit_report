# How to use
1. Clone the repository to your device.
2. Copy the style.html file and place it in the same folder as your dashboard file.
    - Modify your CSS styles as desired (make sure not to delete any).
3. In your program, add the cloned repository location to your path and call the Report class:
```python
import sys
sys.path.insert(<cloned repo location>)
import report
r = report.Report()
```
4. For supported functions (see below), replace _st._ with _r._ and the Report class will call the streamlit function and write to your report simultaneously.
5. Call the download method to add a button to toggle report generation and download: 
```python
r.download()
```
6. Run your dashboard, click the **Generate Report?** button, navigate to each page, activate the content you'd like to add to your report, and click the **Download!** button when done. NOTE: the report overwrites a page's content each time you visit it on the dashboard.

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
- [x] collapsable sidebar
- [ ] reveal the collapsed sidebar
- [ ] _streamlit.cols_ support using **with** generator functions
- [x] _streamlit.altair_chart_ support
- [x] _streamlit_report.Report.ignore_ flag to temporarily suppress writing to the report file
- [x] _streamlit.dataframe_ support, displaying a polars or pandas dataframe in a sized window
- [x] _streamlit.selectbox_ support, displaying the name of the item selected during report generation
- [ ] _streamlit.multiselectbox_ support, displaying the name of the items selected during report generation
- [x] _streamlit.slider_ support for single value slider selections
- [ ] _streamlit.slider_ support for multipoint values selections
- [x] report generation and download button for single page reports
- [x] multi-page app support
- [x] creation of single report for multi-page applications
- [ ] improved style defaults
- [x] option to specify the default page order that a report generates in
- [ ] option to only replace page content when a button is pressed
- [ ] option to write to temporary files instead of storing the html code in memory