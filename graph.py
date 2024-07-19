import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
#import plotly.graph_objects as go

"""
This analysis examines how assessments of certain houses have been affected by Article 34's 
April 2023 amendment to Lexington's Zoning Bylaw.
"""

properties = pd.read_csv ("Data/analysis_data.csv")