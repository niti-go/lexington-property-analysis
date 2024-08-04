import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
#import plotly.graph_objects as go

"""
This file creates the graphs to examine how assessments of properties have been 
affected by Article 34's amendment to Lexington's zoning.
"""
df = pd.read_csv ("Data/analysis_data.csv")

print(df["Building Model"].value_counts())

is_na_value = df["Overlay District"].isna()
df.loc[is_na_value, "Overlay District"] = "Not Multifamily"

#Aggregate buildings into two model types: residential and commercial
# print("Num industrial", len(df[df["Building Model"] == "Industrial"]))
# print("Num Commercial Condo", len(df[df["Building Model"] == "Com Condo"]))
# print("Num Serv station", len(df[df["Building Model"] == "Serv Station"]))
is_commercial = (df["Building Model"] == "Industrial") | (df["Building Model"] == "Com Condo") | (df["Building Model"] == "Serv Station")
is_residential = (df["Building Model"] == "Res Condo")
df.loc[is_commercial, "Building Model"] = "Commercial"
df.loc[is_residential, "Building Model"] = "Residential"

# Seeing that most properties who aren't labeled as residential/commercial 
# do not have assessment data anyway, so it is ok to remove them from analysis
# categoryless = df[df["Building Model"] == " "]
# print(categoryless["Improvements"].isna().sum())
# print(len(categoryless))

#Remove buildings from plot whose building type is na
df = df[df["Building Model"] != " "]

#Remove buildings from plot whose change in value is 0
#since they are likely units that aren't individually assessed
df = df[df["Land"] != 0]

#Our house
# is_our_house = df["Location"] == "street address"
# df.loc[is_our_house, "Overlay District"] = "Our House"

category_order = ["Not Multifamily", "VO", "VHO", "MFO"]

## Percent Change in Land Value Graph
fig1 = px.box(df, x="Overlay District", y="Land", points="all", color="Building Model",
              labels={"Land": "% Change in Land Value"},
              title="2023-2024 % Change in Land Value",
              hover_name="Location",
              category_orders={"Overlay District": category_order})
fig1.update_layout(yaxis_range=[8, 12])  
# fig1.show()

## Percent Change in Improvements Value Graph
fig2 = px.box(df, x="Overlay District", y="Improvements", 
              points="all", color="Building Model",
              labels={"Improvements": "% Change in Improvements Value"},
              title="2023-2024 Percent Change in Assessed Value",
              hover_name="Location",
              category_orders={"Overlay District": category_order})
fig2.update_layout(yaxis_range=[-30, 50])  
#fig2.show()

#-------- Aggregated zoning analysis------------

category_order = ["Not Multifamily", "Multifamily Zoning"]

is_multifamily = (df["Overlay District"] != "Not Multifamily")
df.loc[is_multifamily, "Overlay District"] = "Multifamily Zoning"

## Percent Change in Land Value Graph
fig3 = px.box(df, x="Overlay District", y="Land", points="all", color="Building Model",
              labels={"Land": "% Change in Land Value"},
              title="2023-2024 Percent Change in Land Value",
              hover_name="Location",
              category_orders={"Zoning District": category_order})
fig3.update_layout(yaxis_range=[8, 12])  
fig3.show()

## Percent Change in Improvements Value Graph
fig4 = px.box(df, x="Overlay District", y="Improvements", 
              points="all", color="Building Model",
              labels={"Improvements": "% Change in Improvements Value"},
              title="2023-2024 Percent Change in Improvements Value",
              hover_name="Location",
              category_orders={"Zoning District": category_order})
fig4.update_layout(yaxis_range=[-30, 50])  
fig4.show()

## Percent Change in Total Assessed Value Graph
fig5 = px.box(df, x="Overlay District", y="Total", 
              points="all", color="Building Model",
              labels={"Total": "% Change in Assessed Value"},
              title="2023-2024 Percent Change in Assessed Value",
              hover_name="Location",
              category_orders={"Zoning District": category_order})
fig5.update_layout(yaxis_range=[-30, 60]) 
fig5.show()