'''
Purpose: File to run at the start of the demo.
'''

# Add to path
import os, sys
updir = os.path.dirname(os.getcwd())
print(updir)
sys.path.insert(0, updir)

import streamlit as st
from streamlit_report import report

def init():
    '''Run for each page'''
    r = report.Report(
        pageOrder = ['demo', 'secondPage']
    )