'''
Purpose: File to run at the start of the demo.
'''

import streamlit as st
import report

def init():
    '''Run for each page'''
    r = report.Report(
        pageOrder = ['demo', 'secondPage']
    )