import streamlit_report
import streamlit as st
import test_helper

# Establish the report
r = streamlit_report.Report()

def main():
    r.write("hello world")
    r.download()

if __name__ == '__main__':
    main()