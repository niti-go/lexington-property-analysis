import pandas as pd
import plotly.express as px
from io import StringIO #to convert strings into pandas dataframes
import ast #to convert strings into dictionary

"""
My analysis, as detailed at:
https://docs.google.com/document/d/1KF8kFlDSe3KBEDSXr35-CsaNOgbL1bRXwxx4KPkNl-E/edit?usp=sharing
to examine how assessments of properties have been affected by an amendment to Lexington's zoning.
"""

def prepare_data():
   """
   Prepares the raw scraped property data for further analysis of Lexington's zoning amendment.
   Saves the processed data to Data/analysis_data.csv.
   """
   properties = pd.read_csv ("Data/all_data.csv")
   changes = pd.read_csv("Data/zone_changes.csv")

   #Remove '$' and ',' from current assessment column
   properties["Current Assessment"] = properties["Current Assessment"].str.replace("$","").str.replace(",","")
   properties["Current Assessment"] = pd.to_numeric(properties["Current Assessment"])
   properties = properties.sort_values("Current Assessment")
   properties["Location"] = properties["Location"].str.strip()

   def csv_string_to_df(str):
      df = pd.read_csv(StringIO(str), sep='\s+')
      return df

   #Convert each property's string Valuation History to a pandas dataframe.
   properties["Valuation History"] = properties["Valuation History"].apply(csv_string_to_df)

   #Separate dataframes by houses that have been changed to:
   # - VO: Village Overlay
   # - MFO: Multi-Family Overlay
   # - VHO: Village High-Rise Overlay
   vo_addresses= changes[changes["Overlay District"] == "VO"]
   mfo_addresses= changes[changes["Overlay District"] == "MFO"]
   vho_addresses= changes[changes["Overlay District"] == "VHO"]

   properties["Overlay District"] = None

   def add_overlay_districts(properties, zone_addresses, new_zone):
      """
      For each address in zone_addresses, finds that property's row in 
      the properties dataframe and changes the Overlay District value from None to new_zone.
      """
      print(f"\n\nChanging overlay districts for new zones...")
      #Loop through each house who is being changed to this zone
      for _, row in zone_addresses.iterrows():
         address = row["Site Address"]
         #Find the row that matches this property and modify its overlay district
         condition = properties["Location"] == address
         properties.loc[condition, "Overlay District"] = new_zone

   # Modify the "Overlay District" column of affected properties to their new zone
   add_overlay_districts(properties, vo_addresses, "VO")
   add_overlay_districts(properties, mfo_addresses, "MFO")
   add_overlay_districts(properties, vho_addresses, "VHO")

   #Add some addresses in manually that didn't perfectly have matching names
   vo_ads = ["32 MASSACHUSETTS AVE #1", "32 MASSACHUSETTS AVE #2", "38 MASSACHUSETTS AVE", 
         "40 MASSACHUSETTS AVE", "120 MASSACHUSETTS AVE #120", "120 MASSACHUSETTS AVE #122",
         "134 MASSACHUSETTS AVE #1", "135 MASSACHUSETTS AVE", "136 MASSACHUSETTS AVE #2", 
         "158 - 160 MASSACHUSETTS AVE", "9 LISBETH ST","10 LISBETH ST","11 LISBETH ST",
         "286 MASSACHUSETTS AVE", "292 MASSACHUSETTS AVE","356 MASSACHUSETTS AVE",
         "358 MASSACHUSETTS AVE","410 MASSACHUSETTS AVE #1","410 MASSACHUSETTS AVE #2",
         "418 MASSACHUSETTS AVE","420 MASSACHUSETTS AVE", "343-345 MASSACHUSETTS AVE",
         "365 WALTHAM ST #1","365 WALTHAM ST #2","365 WALTHAM ST #3","365 WALTHAM ST #4",
         "367 WALTHAM ST #5","95-97 BEDFORD ST #95","159 BEDFORD ST","161 BEDFORD ST", 
         "171-173 BEDFORD ST", "193 BEDFORD ST", "195 BEDFORD ST"
         ]
   for i in range(3, 25):
      vo_ads.append(f"{i} LOIS LN")
   properties.loc[properties["Location"].isin(vo_ads), "Overlay District"] = "VO"

   mfo_ads = ["2-4 WALLIS CT #4", "2-4 WALLIS CT #2", "52A WALTHAM ST", "52B WALTHAM ST", 
            "1775 MASSACHUSETTS AVE #1","1775 MASSACHUSETTS AVE #2","1775 MASSACHUSETTS AVE #3",
            "1775 MASSACHUSETTS AVE #4","10 MERIAM ST"]
   for i in range(1, 23):
      mfo_ads.append(f"10 MUZZEY ST #{i}")
   properties.loc[properties["Location"].isin(mfo_ads), "Overlay District"] = "MFO"

   def percent_dif(a, b):
      """
      Returns the percent difference between a and b (presumably dollar amounts), 
      positive if b is larger than a.
      """
      try:
         if pd.isna(a) or pd.isna(b):
            print(f"NaN value encountered: a = {a}, b = {b}")
            return None
         if a == 0 or b == 0:
            #print("One or more of the values is 0.")
            return None
         return ((b - a) / a) * 100
      except Exception as e:
         print(f"Exception in percent_dif: {e}")
         print(f"Values: a = {a}, b = {b}")
         return None


   def assessment_chgs(vh):
      """
      Returns the percent change in a property's improvements, land, and total valuation
      from 2023 to 2024 as a tuple.
      vh must be a Valuation History table with these columns.
      """

      #Remove "$" and "," from entries and convert them to numeric types
      for col in ['Improvements', 'Land', 'Total']:
            vh[col] = vh[col].astype(str).str.replace('[$,]', '', regex=True)
            vh[col] = pd.to_numeric(vh[col], errors="coerce")

      vh["Year"] = pd.to_numeric(vh["Year"])
      from_row = vh[vh["Year"] == 2023]
      to_row = vh[vh["Year"] == 2024]

      if len(from_row) != 1 or len(to_row) != 1: #something's wrong with the valuation history table
         print("Valuation History table doesn't include 2023 and/or 2024")
         #print(vh)
         return (None, None, None)
      
      #iloc[0] essentially converts the 1-element series to just the value
      improv = percent_dif(from_row["Improvements"].iloc[0], to_row["Improvements"].iloc[0]) 
      land = percent_dif(from_row["Land"].iloc[0], to_row["Land"].iloc[0])
      total = percent_dif(from_row["Total"].iloc[0], to_row["Total"].iloc[0])
      return (improv, land, total)

   #Create new column containing information about percent changes in assessments from 2023 to 2024
   properties["All Changes"] = properties["Valuation History"].apply(assessment_chgs)

   #Separate the three calculated percentage values into 3 columns
   properties["Improvements"] = properties["All Changes"].apply(lambda tuple: tuple[0])
   properties["Land"] = properties["All Changes"].apply(lambda tuple: tuple[1])
   properties["Total"] = properties["All Changes"].apply(lambda tuple: tuple[2])

   def get_model_type (str_dict):
      """
      Returns the value of the "Model" key in str_dict, assuming str_dict is a 
      string containing Building Attributes with similar format as: 
      "{"Style": "Colonial", "Model": "Residential", ...}"
      """
      attributes = ast.literal_eval(str_dict)
      return attributes.get("Model")
      
   properties["Building Model"] = properties["Building Attributes"].apply(get_model_type)

   #Save a view of our new columns of interest to a csv for further analysis
   properties[["Location", "Building Model", "Overlay District","Improvements", "Land", "Total"]].to_csv("Data/analysis_data.csv")

def create_graphs():
   """
   Reads the processed data and creates graphs for analysis.
   """
   df = pd.read_csv ("Data/analysis_data.csv")


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

def main():
   #prepare_data()
   create_graphs()

main()