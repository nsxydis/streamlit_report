'''
Purpose: test st.date_input
'''

import streamlit as st
import report
import polars as pl
r = report.Report()

def main():
    r.text_area('area')

    r.text_input('input')

    r.text("This is some text")

    r.download()

if __name__ == '__main__':
    main()