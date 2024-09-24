'''
Purpose: test st.multiselect
'''

import streamlit as st
from streamlit_report import report
import polars as pl
r = report.Report()

def main():
    # List input
    options = ['a', 'b', 'c', 'd']
    sel = r.multiselect('selections', options = options)
    st.write(sel)
    
    # Dataframe input
    df = pl.DataFrame({
        '1' : [1, 2, 3, 4, 5],
        '2' : [4, 5, 6, 7, 8]
    })
    sel2 = r.multiselect('dataframe selections', options = df)
    st.write(sel2)
    st.write(type(sel2))

    r.download()

if __name__ == '__main__':
    main()