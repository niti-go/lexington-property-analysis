import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

import ast #to convert strings into dictionary
import io
import re
import base64
from io import StringIO
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import webbrowser
import sys
import os


def parse_valuation_history(raw):
    """Parses a property's scraped 'Valuation History' string into a sorted
    list of {'year': int, 'total': int}. Returns [] if parsing fails."""
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        table = pd.read_csv(StringIO(raw), sep=r'\s+')
        rows = []
        for _, r in table.iterrows():
            year = int(r["Year"])
            total = int(re.sub(r"[^\d]", "", str(r["Total"])))
            rows.append({"year": year, "total": total})
        return sorted(rows, key=lambda x: x["year"])
    except Exception:
        return []


#Theme colors (pulled from the undraw hero illustration)
THEME_ACCENT = "#6c63ff"       # indigo — "similar" / other properties
THEME_ACCENT_SOFT = "#a7a1ff"  # lighter indigo — trendlines, large-N scatter
THEME_USER = "#ff6584"         # coral — the user's house
THEME_TEXT = "#3f3d56"         # navy — axis labels, titles
THEME_GRID = "#e4e3ec"         # light gray-purple — gridlines
THEME_3D_SCALE = [              # indigo → coral gradient for the 3D plot
    [0.0, "#3f3d56"],
    [0.5, "#6c63ff"],
    [1.0, "#ff6584"],
]
PLOTLY_LAYOUT = dict(
    font=dict(family="-apple-system, Segoe UI, Roboto, sans-serif", color=THEME_TEXT),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

#Load all Lexington property data
_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "all_data.csv")
_HEATMAP_PATH = os.path.join(os.path.dirname(__file__), "static", "correlation_heatmap.png")
df = pd.read_csv(_DATA_PATH)

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

#------------Main Program Logic-------------

def main_program(your_house_row):
    df = globals()["df"]
    print("Debug: Entered main_program")
    print(f"Debug: your_house_row: {your_house_row}")

    #--------Get The User's House--------
    your_loc = your_house_row["Location"]
    print(f"Debug: your_loc: {your_loc}")
    your_bpg = your_house_row["Building Percent Good"]
    print(f"Debug: your_bpg: {your_bpg}")
    your_assessment = your_house_row["Current Assessment"]
    print(f"Debug: your_assessment: {your_assessment}")
    your_yr_blt = your_house_row["Year Built"]
    print(f"Debug: your_yr_blt: {your_yr_blt}")
    your_style = your_house_row["Building Style"]
    print(f"Debug: your_style: {your_style}")
    your_living_area = your_house_row["Living Area"]
    print(f"Debug: your_living_area: {your_living_area}")

    #---------Display Similar Sales Scatterplot--------
    yr_blt = your_house_row["Year Built"]
    nearby_yrs = [i for i in range(yr_blt-7, yr_blt+8)]
    print(f"Debug: nearby_yrs: {nearby_yrs}")
    similar = df[df['Year Built'].isin(nearby_yrs)]
    print(f"Debug: similar properties count: {len(similar)}")

    if (your_style != "Apartments"):
        similar = similar[similar["Building Style"] != "Apartments"]
        print(f"Debug: similar properties after removing apartments: {len(similar)}")

    living_area = your_house_row["Living Area"]
    max_area = living_area+300
    min_area = living_area-300
    similar = similar[(similar['Living Area'] >= min_area) & (similar['Living Area'] <= max_area)]
    print(f"Debug: similar properties after living area filter: {len(similar)}")

    #houses sold this year
    recent_yrs = [2022, 2023, 2024]
    similar_sales = similar[(similar['Sale Year'].isin(recent_yrs))]
    similar_sales = similar_sales[(similar_sales['Sale Price'] > 1000)]
    print(f"Debug: similar_sales count: {len(similar_sales)}")

    # Debugging after similar_sales count
    print(f"Debug: similar_sales DataFrame: {similar_sales}")

    # Check if similar_sales is empty
    if similar_sales.empty:
        print("Debug: similar_sales is empty")
    else:
        print("Debug: similar_sales is not empty")

    # Attempt to create the scatter plot
    try:
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
        print("Debug: Scatter plot created successfully")
    except Exception as e:
        print(f"Debug: Error while creating scatter plot: {e}")
        raise

    # Color scatter points + trendline in theme colors
    fig1.update_traces(selector=dict(mode="markers"),
                       marker=dict(size=10, color=THEME_ACCENT))
    fig1.update_traces(selector=dict(mode="lines"),
                       line=dict(color=THEME_ACCENT_SOFT, width=2))

    # Add the user's house as a coral point
    fig1.add_trace(go.Scatter(
        x=[your_living_area],
        y=[your_assessment],
        mode='markers',
        marker=dict(
            size=12,
            color=THEME_USER,
            line=dict(color="white", width=2),
            opacity=1,
        ),
        name="Your House Assessment",
        text=f"Address: {your_loc}<br>Style: {your_style}<br>Year Built: {your_yr_blt}<br>Building Percent Good: {your_bpg}<br>Assessment: {your_assessment:,}"
    ))

    # Update layout for margin, titles, etc.
    fig1.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        xaxis_title='Living Area (Square Feet)',
        yaxis_title='Sale Price',
        xaxis=dict(gridcolor=THEME_GRID, zerolinecolor=THEME_GRID),
        yaxis=dict(gridcolor=THEME_GRID, zerolinecolor=THEME_GRID),
        **PLOTLY_LAYOUT,
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

    #Compare the user's property assessment to the trendline prediction
    try:
        # Extract the data from the figure
        trendline_data = fig1.data[1]  # Assumes the trendline is the second trace

        # Get x and y values of the trendline
        trendline_x = trendline_data['x']
        trendline_y = trendline_data['y']

        # Calculate slope and intercept
        slope, intercept = np.polyfit(trendline_x, trendline_y, 1)

        # Determine how the actual assessment compares to the predicted assessment
        predicted_price = slope * your_living_area + intercept
        if predicted_price > your_assessment:
            compare_to_trendline = "lower than"
        elif predicted_price < your_assessment:
            compare_to_trendline = "higher than"
        else:
            compare_to_trendline = "equal to"

        fig1text = (
            f"Recent sales of similar homes (built {yr_blt-7}–{yr_blt+8}, {living_area-300}–{living_area+300} sq ft). "
            f"Your property's assessment is {compare_to_trendline} the sale prices of these similar houses. "
            f"If you feel that your property has been overvalued without any distinguishing reason compared to the other houses, you may consider talking to a town official or applying for an abatement."
        )
    except Exception:
        compare_to_trendline = None
        fig1text = (
            f"Recent sales of similar homes (built {yr_blt-7}–{yr_blt+8}, {living_area-300}–{living_area+300} sq ft). "
            f"If you feel that your property has been overvalued without any distinguishing reason compared to the other houses, you may consider talking to a town official or applying for an abatement."
        )

    #fig1.show()

    #Correlation heatmap is pre-computed at module load time (see bottom of file) —
    #the top three features most correlated with assessment value are Living Area,
    #Building Percent Good, and Year Built, which is what this report compares on.

    #------Display All Houses 3D Scatterplot----------

    #Remove outlier houses from df for better scaling and visualization
    df = df[df["Current Assessment"] >= your_assessment-3000000]
    df = df[df["Current Assessment"] <= your_assessment+3000000]
    df = df[df["Living Area"] < your_living_area + 4000]
    df = df[df["Living Area"] > your_living_area - 4000]

    #Plot all houses
    fig2=go.Figure(data=go.Scatter3d(x=df["Living Area"], y=df["Building Percent Good"], z=df["Current Assessment"],
                                    mode='markers', marker=dict(
                                        size=5, color=df["Current Assessment"], colorscale=THEME_3D_SCALE,
                                        opacity=0.7),text=df.apply(lambda row: f"Address: {row['Location']}<br>Style: {row['Building Style']}<br>Year Built: {row['Year Built']}", axis=1), name="Other House"))


    # Add the user's house as a coral point
    fig2.add_trace(go.Scatter3d(
        x=[your_living_area],
        y=[your_bpg], #building percent good
        z=[your_assessment],
        mode='markers',
        marker=dict(
            size=10,
            color=THEME_USER,
            line=dict(color="white", width=2),
            opacity=1,
        ),
        name='Your House',
        text=your_loc
    ))

    #Set axis titles and formatting
    fig2.update_layout(margin=dict(l=0, r=0, b=0, t=40),
                    scene=dict(
            xaxis_title='Living Area (Square Feet)',
            yaxis_title='Building Percent Good',
            zaxis_title='2024 Assessment Value',
            xaxis=dict(gridcolor=THEME_GRID, backgroundcolor="white"),
            yaxis=dict(gridcolor=THEME_GRID, backgroundcolor="white"),
            zaxis=dict(gridcolor=THEME_GRID, backgroundcolor="white"),
        ),
        title="All(*) Lexington Residences",
        **PLOTLY_LAYOUT,
    )


    # #Add caption that I removed outliers for cleaner visualization
    # fig2.add_annotation(
    #     text='(*) Removed outliers for clearer visualization.\nHover over a property to view details.',
    #     xref="paper", yref="paper",
    #     x=0.5, y=-0.1, showarrow=False,
    #     font=dict(size=12)
    # )

    fig2text = (
        "Explore all Lexington residences plotted by Living Area, Building Percent Good, and Assessment Value. "
        "Hover over any point to see that property's details. "
        "If you feel that your property is an outlier without any distinguishing reason compared to the other houses, you may consider talking to a town official or applying for an abatement."
    )

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
        hover_data=["Location", "Year Built", "Living Area", "Building Percent Good", "Building Style"],
        color_discrete_sequence=[THEME_ACCENT],
    )
    fig3.update_layout(
        xaxis=dict(gridcolor=THEME_GRID),
        yaxis=dict(gridcolor=THEME_GRID, zerolinecolor=THEME_GRID),
        **PLOTLY_LAYOUT,
    )

    # Add a single trace for the user's house
    fig3.add_trace(
        go.Scatter(
            x=["Similar Lexington Properties"],  # Box plots in Plotly don't use x-axis values, so this can be a dummy value
            y=[your_assessment],
            mode='markers',
            marker=dict(
                size=12,
                color=THEME_USER,
                line=dict(color="white", width=2),
                opacity=1,
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

    fig3text = (
        f"All similar Lexington properties by 2024 assessment value. Your property's assessment is {comparison} "
        f"If you feel that your property has been overvalued without any distinguishing reason compared to the other houses, you may consider talking to a town official or applying for an abatement."
    )

    analysis_text = (
        "Based on the data analysis behind this report, the features most correlated with a property's assessment "
        "are Living Area, Building Percent Good, and Year Built. Many other factors also affect assessment — "
        "floor plan, kitchen style, number of rooms, energy efficiency, proximity to the town center and highways, "
        "and historical value — that aren't captured here. "
        "For a fuller picture of any property, see the"
    )

    #--------Headline verdict: rank and percentile vs similar properties--------
    similar_assessments = similar["Current Assessment"].dropna()
    num_similar = len(similar_assessments)
    rank = int((similar_assessments > your_assessment).sum()) + 1
    percentile = int(round((similar_assessments <= your_assessment).mean() * 100)) if num_similar else 0
    median_similar = int(similar_assessments.median()) if num_similar else 0
    pct_vs_median = ((your_assessment - median_similar) / median_similar * 100) if median_similar else 0

    if pct_vs_median >= 5:
        verdict_headline = f"~{abs(int(round(pct_vs_median)))}% higher than the median for similar homes"
    elif pct_vs_median <= -5:
        verdict_headline = f"~{abs(int(round(pct_vs_median)))}% lower than the median for similar homes"
    else:
        verdict_headline = "close to the median for similar homes"

    verdict = {
        "headline": verdict_headline,
        "rank": rank,
        "num_similar": num_similar,
        "percentile": percentile,
        "median_similar": median_similar,
        "yr_range": f"{yr_blt-7}\u2013{yr_blt+8}",
        "area_range": f"{living_area-300:,}\u2013{living_area+300:,}",
    }

    #--------Top 3 most similar recent sales (closest in living area)--------
    comparables = []
    if not similar_sales.empty:
        closest = similar_sales.assign(
            area_diff=(similar_sales["Living Area"] - your_living_area).abs()
        ).sort_values("area_diff").head(3)
        for _, row in closest.iterrows():
            sale_date = row["Sale Date"]
            comparables.append({
                "location": row["Location"],
                "sale_price": int(row["Sale Price"]),
                "sale_year": int(row["Sale Year"]) if pd.notna(row["Sale Year"]) else None,
                "living_area": int(row["Living Area"]),
                "year_built": int(row["Year Built"]),
                "style": row["Building Style"],
                "assessment": int(row["Current Assessment"]),
            })

    #--------Valuation history sparkline data--------
    valuation_history = parse_valuation_history(your_house_row.get("Valuation History"))

    return {
        "your_loc": your_loc,
        "your_assessment": your_assessment,
        "your_yr_blt": your_yr_blt,
        "your_living_area": your_living_area,
        "your_style": your_style,
        "your_bpg": your_bpg,
        "fig1": fig1,
        "fig1text": fig1text,
        "fig2": fig2,
        "fig2text": fig2text,
        "fig3": fig3,
        "fig3text": fig3text,
        "analysis_text": analysis_text,
        "verdict": verdict,
        "comparables": comparables,
        "valuation_history": valuation_history,
    }


#----------- Pre-compute correlation heatmap once at module load -----------
def _generate_correlation_heatmap():
    """Generates the correlation heatmap PNG once, themed to match the site."""
    if os.path.exists(_HEATMAP_PATH):
        return
    numeric_df = df.select_dtypes(include='number')
    if "Unnamed: 0" in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=["Unnamed: 0"])
    corr_matrix = numeric_df.corr()
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "theme", [THEME_ACCENT, "#ffffff", THEME_USER]
    )
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(
        corr_matrix, annot=True, cmap=cmap, fmt='.2f',
        vmin=-1, vmax=1, linewidths=0.5, linecolor="white",
        cbar_kws={"shrink": 0.8}, annot_kws={"size": 8}, ax=ax,
    )
    ax.tick_params(colors=THEME_TEXT, labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    os.makedirs(os.path.dirname(_HEATMAP_PATH), exist_ok=True)
    plt.savefig(_HEATMAP_PATH, dpi=130, bbox_inches='tight')
    plt.close(fig)


_generate_correlation_heatmap()


# ----------- Standalone Local Script -----------
def main():
    print("Welcome to the Lexington Property Report Generator!")
    address = input("Enter your property address (as it appears in the database): ").strip().upper()
    house_row = df[df['Location'] == address]
    if house_row.empty:
        print("Error: The entered property address does not exist in the database.")
        sys.exit(1)
    house_row = house_row.iloc[0]
    print(f"Generating report for {address}...")
    result = main_program(house_row)
    your_loc = result["your_loc"]
    your_assessment = result["your_assessment"]
    your_yr_blt = result["your_yr_blt"]
    your_living_area = result["your_living_area"]
    your_style = result["your_style"]
    your_bpg = result["your_bpg"]
    fig1 = result["fig1"]; fig1text = result["fig1text"]
    fig2 = result["fig2"]; fig2text = result["fig2text"]
    fig3 = result["fig3"]; fig3text = result["fig3text"]
    analysis_text = result["analysis_text"]

    html_content = f"""
    <html>
    <head>
        <title>Property Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
            h1 {{ color: #333; }}
            p {{ margin: 10px 0; }}
            .section {{ margin-bottom: 20px; }}
            .chart {{ margin: 20px 0; max-width: 800px; margin-left: auto; margin-right: auto; }}
            .caption {{ font-size: 0.9em; color: grey; margin-top: 10px; margin-bottom: 10px; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Property Report (2023-2024) for {your_loc}</h1>
        <div class="section">
            <h2>Property Details</h2>
            <p><strong>Assessment:</strong> {your_assessment}</p>
            <p><strong>Year Built:</strong> {your_yr_blt}</p>
            <p><strong>Living Area:</strong> {your_living_area} sq ft</p>
            <p><strong>Style:</strong> {your_style}</p>
            <p><strong>Building Percent Good:</strong> {your_bpg}%</p>
        </div>
        <div class="section">
            <h2>Analysis</h2>
            <p>{analysis_text}</p>
        </div>
        <div class="section chart">
            <h2>Recent Similar House Sales</h2>
            {fig1.to_html(full_html=False)}
            <p class="caption">{fig1text}</p>
        </div>
        <div class="section chart">
            <h2>All Lexington Residences</h2>
            {fig2.to_html(full_html=False)}
            <p class="caption">{fig2text}</p>
        </div>
        <div class="section chart">
            <h2>Similar Properties Assessments</h2>
            {fig3.to_html(full_html=False)}
            <p class="caption">{fig3text}</p>
        </div>
    </body>
    </html>
    """
    output_file = "property_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Report generated: {output_file}")
    webbrowser.open(f"file://{os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()