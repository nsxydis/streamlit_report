'''
Purpose: Be the first page of the report
'''
import streamlit_report
r = streamlit_report.Report()

r.write("hello world -- front page, here I am.")
r.download()