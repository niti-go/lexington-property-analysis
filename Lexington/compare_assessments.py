import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ast #to convert strings into dictionary
#For displaying graphs
import dash
from dash import dcc, html
import io
import base64
import statsmodels

#Load all Lexington property data
df = pd.read_csv ("Data/all_data.csv")

#Initializing global variables
fig1 = fig2 = fig3 = 0
fig1text = fig2text = fig3text = analysis_text = ""

def get_model_type (str_dict):
        """
        Returns the values of the "Model" key in str_dict, assuming str_dict is a 
        string containing Building Attributes with similar format as: 
        "{"Style": "Colonial", "Model": "Residential", ...}"
        """
        attributes = ast.literal_eval(str_dict)
        return attributes.get("Model")

#Add a column for building model (e.g commerical, residential, industrial)
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
df["Location"] = df["Location"].str.strip()

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


app = dash.Dash(__name__)
print("app created")

def main_program(your_house_row):
    global fig1
    global fig2
    global fig3
    global fig1text
    global fig2text
    global fig3text
    global analysis_text
    global df

    #--------Get The User's House--------
    #your_house_row = get_user_address(df)
    your_loc = your_house_row["Location"]
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

    #Unless the user's property is an apartment, remove apartments from 
    #dataframe as these are outliers with extreme assessments, and are not individual residences.
    if (your_style != "Apartments"):
        similar = similar[similar["Building Style"] != "Apartments"]

    living_area = your_house_row["Living Area"]
    max_area = living_area+300  
    min_area = living_area-300  
    similar = similar[(similar['Living Area'] >= min_area) & (similar['Living Area'] <= max_area)]

    #houses sold this year
    recent_yrs = [2022, 2023,2024]
    similar_sales = similar[(similar['Sale Year'].isin(recent_yrs))]
    similar_sales = similar_sales[(similar_sales['Sale Price'] > 1000)] #Remove transactions
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
        title = "Recent Sale Prices of Similar Properties"
                    )

    # Add the user's house as a yellow point
    fig1.add_trace(go.Scatter(
        x=[your_living_area],
        y=[your_assessment],
        mode='markers',
        marker=dict(
            size=10,
            color='goldenrod',
            opacity=0.9
        ),
        name="Your House Assessment",
        text=f"Address: {your_loc}<br>Style: {your_style}<br>Year Built: {your_yr_blt}<br>Building Percent Good: {your_bpg}"
    ))

    # -----graph using px----
    # Create the scatter plot with a trendline
    fig1 = px.scatter(
        similar_sales,
        x="Living Area",
        y="Sale Price",
        trendline="ols",
        title="Recent Similar House Sales",
        labels={"Living Area": "Living Area (Square Feet)", "Sale Price": "Sale Price"},
        opacity=0.8,
        hover_data={
            'Location': True, 
            'Building Style': True, 
            'Year Built': True, 
            'Building Percent Good': True, 
            'Current Assessment': True
        }
    )

    # Update the color of the points to purple
    fig1.update_traces(marker=dict(size=10, color='purple'))

    # Add the user's house as a yellow point
    fig1.add_trace(go.Scatter(
        x=[your_living_area],
        y=[your_assessment],
        mode='markers',
        marker=dict(
            size=10,
            color='goldenrod',
            opacity=0.9
        ),
        name="Your House Assessment",
        text=f"Address: {your_loc}<br>Style: {your_style}<br>Year Built: {your_yr_blt}<br>Building Percent Good: {your_bpg}<br>Assessment: {your_assessment:,}"
    ))

    # Update layout for margin, titles, etc.
    fig1.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        xaxis_title='Living Area (Square Feet)',
        yaxis_title='Sale Price',
    )

    x_value_min = similar_sales['Living Area'].min() - 50
    x_value_max = similar_sales['Living Area'].max() + 50

    fig1.update_xaxes(range=[x_value_min, x_value_max])

    # #Add caption
    # fig1.add_annotation(
    #     text='Caption', yref="paper",
    #     x=0.5, y=-0.1, showarrow=False,
    #     font=dict(size=12)
    # )

    # Extract trendline data
    trendline_data = fig1.data[1]
    trendline_x = trendline_data.x
    trendline_y = trendline_data.y
    predicted_price = trendline_x * your_living_area + trendline_y

    if predicted_price.all() > your_assessment.all():
        compare_to_trendline = "lower than"
    elif predicted_price.all() < your_assessment.all():
        compare_to_trendline = "higher than"
    else:
        compare_to_trendline = "equal to"

    fig1text = \
    f"""
    "All recent sales and market prices of similar properties built between {yr_blt-7} and {yr_blt+8}, with living areas between {living_area-300} and {living_area+300} square feet. Your property's assessment is {compare_to_trendline} the prices of these other similar houses."
    If you feel that your property has been overvalued without any distinguishing reason compared to the other houses, you may consider talking to a town official or applying for an abatement.
    """

    #fig1.show()

    #------Correlation Heatmap-------- 
    numeric_df = df.select_dtypes(include='number')
    corr_matrix = numeric_df.corr()
    heatmap = sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')

    #Save the heatmap as a base64 image so it can be displayed later on the website
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()

    #plt.show()
    #The features most correlated with assessment are Living Area, Building Percent Good, and Year Built

    #------Display All Houses 3D Scatterplot----------

    #Remove outlier houses from df for better scaling and visualization
    df = df[df["Current Assessment"] >= your_assessment-3000000]
    df = df[df["Current Assessment"] <= your_assessment+3000000]
    df = df[df["Living Area"] < your_living_area + 4000]
    df = df[df["Living Area"] > your_living_area - 4000]

    #Plot all houses
    fig2=go.Figure(data=go.Scatter3d(x=df["Living Area"], y=df["Building Percent Good"], z=df["Current Assessment"], 
                                    mode='markers', marker=dict(
                                        size=10, color=df["Current Assessment"], colorscale='plotly3',
                                        opacity=0.8, reversescale=True),text=df.apply(lambda row: f"Address: {row['Location']}<br>Style: {row['Building Style']}<br>Year Built: {row['Year Built']}", axis=1), name="Other House"))


    # Add the user's house as a yellow point
    fig2.add_trace(go.Scatter3d(
        x=[your_living_area],
        y=[your_bpg], #building percent good
        z=[your_assessment],
        mode='markers',
        marker=dict(
            size=10,
            color='goldenrod',
            opacity=0.9
        ),
        name='Your House',
        text=your_loc
    ))

    #Set axis titles and formatting
    fig2.update_layout(margin=dict(l=0, r=0, b=0, t=40),
                    scene=dict(
            xaxis_title='Living Area (Square Feet)',
            yaxis_title='Building Percent Good',
            zaxis_title='2024 Assessment Value'
        ), 
        title = "All(*) Lexington Residences"
                    )


    # #Add caption that I removed outliers for cleaner visualization
    # fig2.add_annotation(
    #     text='(*) Removed outliers for clearer visualization.\nHover over a property to view details.',
    #     xref="paper", yref="paper",
    #     x=0.5, y=-0.1, showarrow=False,
    #     font=dict(size=12)
    # )

    fig2text = \
    f"""
    (*)Removed outliers for a clearer visualization.
    Hover over a property to view details.
    """

    #fig2.show()
    #----------Boxplot-------------

    #The dataframe containing houses built around same time period
    #with similar living area is named "similar" (from above)
    have_apartments = similar[similar["Building Style"] == "Apartments"]

    # Add a dummy column to the DataFrame
    similar['Category'] = 'Similar Lexington Properties'

    # Create the box plot
    fig3 = px.box(
        similar,
        x="Category",
        y="Current Assessment",
        points="all",
        labels={"y": "2024 Assessment", "Category": ""},
        title="All Similar Properties Assessments",
        hover_name="Location",
        hover_data=["Location", "Year Built", "Living Area", "Building Percent Good", "Building Style"]
    )

    # Add a single trace for the user's house
    fig3.add_trace(
        go.Scatter(
            x=["Similar Lexington Properties"],  # Box plots in Plotly don't use x-axis values, so this can be a dummy value
            y=[your_assessment],
            mode='markers',
            marker=dict(
                size=10,
                color='goldenrod',
                opacity=0.9
            ),
            name='Your House',
            text=f"Location: {your_loc}<br>Year Built: {your_yr_blt}<br>Living Area: {your_living_area}<br>Building Percent Good: {your_bpg}<br>Building Style: {your_style}"
        )
    )

    #Compare the user's house assessment to the median, 1st quartile, and 3rd quartile
    median = similar["Current Assessment"].median()
    q1 = similar['Current Assessment'].quantile(0.25)
    q3 = similar['Current Assessment'].quantile(0.75)
    if your_assessment <= q1:
        comparison = "somewhat lower than others."
    elif your_assessment < median:
        comparison = "slightly lower than the median."
    elif your_assessment < q3:
        comparison = "slightly greater than the median."
    else:
        comparison = "somewhat greater than others."

    fig3text = \
    f"""
    Lexington's assessment designations of all similar properties, built around the same time period as your property with similar living area measurements.\
    Hover over a property to view details.

    Your property's assessment is {comparison}

    Note: Comparing your property to the median may not lead to an accurate conclusion, as there may be more properties in one extreme of the living area range, skewing the results.
    """

    analysis_text = \
    """
    Some background behind this report:
    The features most correlated with Assessment are Living Area, Building Percent Good, and Year Built, as seen in the heatplot below.
    However, there are many other factors that affect assessment that are not captured in this report, including floor plan layout, kitchen style, number of rooms, extra features such as energy efficiency, distance to the town center and major highways, and historical value.
    For a more holistic understanding of these factors for any house, you can view the Assessor's Database at https://gis.vgsi.com/lexingtonma/.
    """

    return your_loc, your_assessment, your_yr_blt, your_living_area, your_style, your_bpg

#------------Display Graphs---------

# app.layout = html.Div([
#     html.H1("Test Layout"),
#     html.P("This is a test paragraph.")
# ])


def create_layout(your_loc, your_assessment, your_yr_blt, your_living_area, your_style, your_bpg):
    return html.Div([
        html.H1(f"{your_loc.title()} Assessment Report"),
        html.H5(f"Created by Niti Goyal"),
        html.H4(f"2024 Assessment: ${your_assessment:,.2f}"),
        html.H4(f"Year Built: {your_yr_blt}"),
        html.H4(f"Living Area (Sq. Feet): {your_living_area:,}"),
        html.H4(f"Building Style: {your_style}"),
        html.H4(f"Building Percent Good: {your_bpg}%"),

        dcc.Graph(figure=fig3), #Boxplot
        html.P(fig3text),
        dcc.Graph(figure=fig1), #Recent Sales
        html.P(fig1text),
        dcc.Graph(figure=fig2), #All Properties
        html.P(fig2text),
        html.P(analysis_text),
        #html.Div([html.Img(src=f"data:image/png;base64,{img_str}")])
    ])

if __name__ == '__main__':
    def get_user_address(df):
        """
        Asks the user for their Lexington property address 
        and returns the relevant property rows from df.
        Repeatedly asks until a valid address is provided.
        """
        your_loc = input("Enter your Lexington property address (e.g. 10 Main St): ").upper()
        try:
            house_row = df[df['Location'] == your_loc].iloc[0]
            return house_row
        except Exception as e:
            print("Couldn't find your house in Lexington's database.")
            return get_user_address(df)

    house_row = get_user_address(df)

    your_loc, your_assessment, your_yr_blt, your_living_area, your_style, your_bpg = main_program(house_row)
    app.layout = create_layout(your_loc, your_assessment, your_yr_blt, your_living_area, your_style, your_bpg)
    app.run_server(debug=True)