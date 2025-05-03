import streamlit_report
import test_helper

# Establish the report
r = streamlit_report.Report()

def main():
    r.write('second page')
    r.download()

if __name__ == '__main__':
    main()