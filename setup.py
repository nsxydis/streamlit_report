'''
setup.py - setup script for streamlit_report 

Copyright 2024 Nick Xydis

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import os
from setuptools import setup

# Setup Function
setup(
    name                = 'streamlit_report',
    version             = '0.0.3',
    description         = 'Package used to create reports from streamlit dashboards',
    long_description    = "See README.md on github url",
    author              = 'Nick Xydis',
    license             = 'Apache License, Version 2.0',
    url                 = 'https://github.com/nsxydis/streamlit_report',

    # Packages
    include_package_data    = True,
    
    # Module requirements
    install_requires    = [
        'streamlit',
        'polars',
        'altair',
        'markdown'
    ]
)