from numba import njit
import math
import numpy as np
from project_src_package_2025.system_configuration import sys_config
from project_src_package_2025.auxiliary_tools import unit_conversion_functions as uni
import pandas as pd


'''
    Configuration of dependencies for computational_tools
'''

# storing dependency titles/aliases which can be accessed across this package
__all__ = ['math', 'njit', 'np', 'pd', 'uni']
