'''
Purpose: test st.slider for range selections
'''

import streamlit as st
from streamlit_report import report
import polars as pl
r = report.Report()

def main():
    a = r.slider(
        'label',
        min_value = 0,
        max_value = 100,
        value = (25, 50)
    )
    st.write(a)

    r.download()    

if __name__ == '__main__':
    main()