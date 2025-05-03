'''
Purpose: Test a basic multipage application using the newer navigation functions.
'''
import streamlit_report
r = streamlit_report.Report()

# Streamlit demo code
import streamlit as st

create_page = st.Page("page_a.py", title="Front page", icon=":material/add_circle:")
delete_page = st.Page("page_b.py", title="Next page", icon=":material/delete:")

pg = r.navigation([create_page, delete_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()


# def main():
#     r.write("# ")

# if __name__ == '__main__':
#     main()