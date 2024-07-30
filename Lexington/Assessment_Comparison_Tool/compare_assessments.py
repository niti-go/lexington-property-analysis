import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ast #to convert strings into dictionary

#Load all Lexington property data
df = pd.read_csv ("Data/all_data.csv")

#Add a column for building model (e.g commerical, residential, industrial)
def get_model_type (str_dict):
   """
   Returns the values of the "Model" key in str_dict, assuming str_dict is a 
   string containing Building Attributes with similar format as: 
   "{"Style": "Colonial", "Model": "Residential", ...}"
   """
   attributes = ast.literal_eval(str_dict)
   return attributes.get("Model")

df["Building Model"] = df["Building Attributes"].apply(get_model_type)

#a dictionary mapping building style abbreviations to the full name
style_mapping = {
    'TRAD/GAR COL.': 'Traditional/Garrison Colonial',
    'CONTP. COL.': 'Contemporary Colonial',
    'Vacant Land': 'Vacant Land',
    'CAPE/GAMBREL': 'Cape Cod/Gambrel',
    'CONDO RESID.': 'Condominium Residential',
    'SMALL CONV.': 'Small Conventional',
    'RANCH': 'Ranch',
    'CONTEMP.': 'Contemporary Design',
    'SE/RR': 'Split-Entry/Raised Ranch',
    'LARGE CONV.': 'Large Conventional',
    'MULTI LEVEL': 'Multi-Level',
    'EST/MAN/LRG': 'Estate/Mansion/Large',
    'DUTCH COL.': 'Dutch Colonial',
    '2&3 FAM SMALL': '2 & 3 Family Small',
    'BUNGLW/OTHER': 'Bungalow/Other',
    '2-3 FAM MED LR': '2-3 Family Dwelling Large',
    'OUTBUILDINGS': 'Outbuildings',
    'APARTMENTS': 'Apartments',
    'MIXED-USE RES': 'Mixed-Use Residence',
    'OUTBLDGS': 'Outbuildings',
    'DAY CARE': 'Day Care',
    'Other Municip': 'Other Municipal',
    'CHURCH': 'Church',
    'PRIV. SCHOOL': 'Private School'
}

#Add a column for building style (e.g commerical, residential, industrial)
def get_style_type (str_dict):
   """
   Returns the values of the "Style" key in str_dict, assuming str_dict is a 
   string containing Building Attributes with similar format as: 
   "{"Style": "Colonial", "Model": "Residential", ...}"
   """
   attributes = ast.literal_eval(str_dict)
   style = style_mapping.get(attributes.get("Style:"))
   return style

df["Building Style"] = df["Building Attributes"].apply(get_style_type)

#Remove commerical properties, we're only interested in residences
residential_models = ["Residential", "", " ", "Res Condo"]
df = df[df["Building Model"].isin(residential_models)]

#Convert sale date to date-time format and create column for sale year
df['Sale Date'] = pd.to_datetime(df['Sale Date'])
df["Sale Year"] = df["Sale Date"].dt.year

#Remove '$' and ',' from the current assessment column
df["Current Assessment"] = df["Current Assessment"].str.replace("$","").str.replace(",","")
df["Current Assessment"] = pd.to_numeric(df["Current Assessment"])
df = df.sort_values("Current Assessment")
df["Sale Price"] = df["Sale Price"].str.replace("$","").str.replace(",","")
df["Sale Price"] = pd.to_numeric(df["Sale Price"])

df["Living Area"] = df["Living Area"].str.replace(",","")
df["Living Area"] = pd.to_numeric(df["Living Area"])
df["Building Percent Good"] = pd.to_numeric(df["Building Percent Good"])

df["Year Built"] = pd.to_numeric(df["Year Built"], errors="coerce").fillna(0).astype(int)

#--------Get The User's House--------

while True: #Keep asking until a valid address is provided
    your_loc = input("Enter your property address (e.g. 10 Main St): ").upper()
    try:
      your_house_row = df[df['Location'] == your_loc].iloc[0]
      df["Highlight"] = df["Location"] == your_loc
      break  # Exit the loop if no exception occurs
    except Exception as e:
      print("Couldn't find your house in Lexington's database.")

your_bpg = your_house_row["Building Percent Good"]
your_assessment = your_house_row["Current Assessment"]
your_yr_blt = your_house_row["Year Built"]
your_style = your_house_row["Building Style"]
your_living_area = your_house_row["Living Area"]


#---------Display Similar Sales Scatterplot--------

#Get all houses with similar Living Area and Year Built that sold in the past year.
yr_blt = your_house_row["Year Built"]
nearby_yrs = [i for i in range(yr_blt-7, yr_blt+8)] #built within +/- 7 years of user's house
similar = df[df['Year Built'].isin(nearby_yrs)]
print(f"Houses built around the same time: {len(similar)}")

living_area = your_house_row["Living Area"]
max_area = living_area+300  
min_area = living_area-300  
similar = similar[(similar['Living Area'] >= min_area) & (similar['Living Area'] <= max_area)]
print(f"Houses built around the same time with similar area: {len(similar)}")

#houses sold this year
recent_yrs = [2022, 2023,2024]
similar_sales = similar[(similar['Sale Year'].isin(recent_yrs))]
similar_sales = similar_sales[(similar_sales['Sale Price'] > 1000)] #Remove transactions
print(f"Sold this year: {len(similar_sales)}")
#print(similar_sales[["Location", "Living Area", "Year Built", "Sale Year", "Sale Price", "Current Assessment"]])

#Plot similar houses
fig1=go.Figure(data=go.Scatter(x=similar_sales["Living Area"], y=similar_sales["Sale Price"], 
                                mode='markers', marker=dict(
                                       size=10, color='purple',
                                       opacity=0.8, reversescale=True),text=similar_sales.apply(lambda row: f"Address: {row['Location']}<br>Style: {row['Building Style']}<br>Year Built: {row['Year Built']}<br>Building Percent Good: {row['Building Percent Good']}<br>Year Sold: {row['Sale Year']}<br>Sale Price: {row['Sale Price']}", axis=1), name="Recent Sale"))

#Set axis titles and formatting
fig1.update_layout(margin=dict(l=0, r=0, b=0, t=40),
        xaxis_title='Living Area (Square Feet)',
        yaxis_title='Sale Price',
    title = "Recent Similar House Sales"
                  )

# Add the user's house as a yellow point
fig1.add_trace(go.Scatter(
    x=df[df["Highlight"] == True]["Living Area"],
    y=df[df["Highlight"] == True]["Current Assessment"],
    mode='markers',
    marker=dict(
        size=10,
        color='goldenrod',
        opacity=0.9
    ),
    name="Your House Assessment",
    text=f"Address: {your_loc}<br>Style: {your_style}<br>Year Built: {your_yr_blt}<br>Building Percent Good: {your_bpg}"
))

fig1.show()

#------Correlation Heatmap-------- 
numeric_df = df.select_dtypes(include='number')
corr_matrix = numeric_df.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.show()
#The features most correlated with assessment are Living Area, Building Percent Good, and Year Built

#------Display All Houses 3D Scatterplot----------

#remove outlier houses from df for better scaling and visualization

df = df[df["Current Assessment"] >= your_assessment-1500000]
df = df[df["Current Assessment"] <= your_assessment+1500000]

df = df[df["Living Area"] < your_living_area + 2000]
df = df[df["Living Area"] > your_living_area - 2000]

#Plot all houses
fig2=go.Figure(data=go.Scatter3d(x=df["Living Area"], y=df["Building Percent Good"], z=df["Current Assessment"], 
                                mode='markers', marker=dict(
                                       size=10, color=df["Current Assessment"], colorscale='plotly3',
                                       opacity=0.8, reversescale=True),text=df.apply(lambda row: f"Address: {row['Location']}<br>Style: {row['Building Style']}<br>Year Built: {row['Year Built']}", axis=1), name="Other House"))

#Set axis titles and formatting
fig2.update_layout(margin=dict(l=0, r=0, b=0, t=40),
                  scene=dict(
        xaxis_title='Living Area (Square Feet)',
        yaxis_title='Building Percent Good',
        zaxis_title='2024 Assessment Value'
    ), 
    title = "All(*) Lexington Residences"
                  )

#Add caption that I removed outliers for cleaner visualization
fig2.update_layout(annotations=[
    dict(
        text='(*) Removed outliers for clearer visualization', 
        x=0.5,
        y=-0.1,
        showarrow=False,
        xref='paper',
        yref='paper'
    )
])
# Add the user's house as a yellow point
fig2.add_trace(go.Scatter3d(
    x=df[df["Highlight"] == True]["Living Area"],
    y=df[df["Highlight"] == True]["Building Percent Good"],
    z=df[df["Highlight"] == True]["Current Assessment"],
    mode='markers',
    marker=dict(
        size=10,
        color='goldenrod',
        opacity=0.9
    ),
    name='Your House',
    text=your_loc
))

fig2.show()
#----------Boxplot-------------

#The dataframe containing with houses built around same time period
#with similar living area is named "similar" (from above)

fig3 = px.box(similar, y="Current Assessment", 
              points="all", color="Living Area",
              labels={"y": "2024 Assessment"},
              title="Assessments of Similar Properties",
              hover_name="Location",
              hover_data=["Year Built", "Living Area", "Building Percent Good", "Building Style"]
              )
#fig3.update_layout(yaxis_range=[-30, 50])  

# Add caption
fig3.add_annotation(
    text="These properties were built around the same time period and have similar living area measurements.",
    xref="paper", yref="paper",
    x=0.5, y=-0.1, showarrow=False,
    font=dict(size=12)
)

fig3.show()

plt.figure(figsize=(4, 6))
vals,names,xs = [],[],[]
vals.append(similar["Current Assessment"].values)
names=["Current Assessment"]
xs.append(np.random.normal(1, 0.01,len(vals[0])))

plt.boxplot(vals,labels=names)
palette = ['m']
y_length = len(vals)
#xs = [1 for i in range (y_length)]
for x, val, c in zip(xs, vals, palette):
  plt.scatter(x, val, alpha=0.4, color=c)

#Add our house
plt.scatter(1, 2396000, alpha=0.9, color = "mediumseagreen",s=100)
plt.show()

#---------Second boxplot--------

fig = px.box(df, x='Category', y='Value', points='all')
fig.show()