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
df = pd.read_csv ("Data/analysis_data.csv")

print(df["Building Model"].value_counts())

is_na_value = df["Overlay District"].isna()
df.loc[is_na_value, "Overlay District"] = "None"

#Aggregate buildings into two model types: residential and commercial
is_commercial = (df["Building Model"] == "Industrial") | (df["Building Model"] == "Com Condo") | (df["Building Model"] == "Serv Station")
is_residential = (df["Building Model"] == "Res Condo")
df.loc[is_commercial, "Building Model"] = "Commercial"
df.loc[is_residential, "Building Model"] = "Residential"

#Remove buildings from plot whose building type is na
df = df[df["Building Model"] != " "]

#Remove buildings from plot whose change in value is 0
#since they are likely units that aren't individually assessed
df = df[df["Land"] != 0]

#Our house
is_our_house = df["Location"] == "24 PHILIP RD"
df.loc[is_our_house, "Overlay District"] = "Our House"

category_order = ["Our House","None", "VO", "VHO", "MFO"]

fig1 = px.box(df, x="Overlay District", y="Land", points="all", color="Building Model",
              labels={"Land": "Percent Change in Land Value"},
              title="Percent Change in Lexington Property Assessed Values From 2023 to 2024",
              hover_name="Location",
              category_orders={"Overlay District": category_order})
fig1.update_layout(yaxis_range=[8, 12])  
fig1.show()

fig2 = px.box(df, x="Overlay District", y="Improvements", 
              points="all", color="Building Model",
              labels={"Improvements": "Percent Change in Improvements Value"},
              title="Percent Change in Lexington Property Assessed Values From 2023 to 2024",
              hover_name="Location",
              category_orders={"Overlay District": category_order})
fig2.update_layout(yaxis_range=[-30, 50])  
fig2.show()

