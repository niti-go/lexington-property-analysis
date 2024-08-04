# Lexington Property Assessment Tool and Zoning Amendment Analysis

I scraped the data of over 12,000 properties from the Town of Lexington's [Public Assessor's Database](https://gis.vgsi.com/lexingtonma/), and used this data for two purposes:

1. Generate a report for any resident that provides analysis for how their property's assessment compares to other properties. [Here is a demo report](https://drive.google.com/file/d/1iagSQqS7lPHBU__Hr9S5rEggr4MWOAqH/view?usp=sharing).

2. Analyze the impact of a 2023 [zoning amendment](https://www.lexingtonma.gov/DocumentCenter/View/8696/Article-34-Motion-combined?bidId=) to the assessed values of affected properties. [Read my analysis here](Results/Zoning_Analysis_Findings.pdf).

## Why I built this project

Living in Lexington, I noticed our property tax increased significantly from 2023 to 2024, despite no changes to our house. I wanted to determine if this was part of a town-wide trend or unique to our property; if it was the latter, this data could help us file an abatement and possibly reduce our taxes. I later realized I could extend this tool to be helpful for any Lexington resident.

I was also curious about the impact of zoning changes, such as that required by MA's 2023 law, to a property's value. [I wrote about my research and analysis here.](Results/Zoning_Analysis_Findings.pdf)

## What I learned

- Web scraping the town's database, collecting data on 35+ features per property. 
- How to implement multithreading to reduce the web scraping time from 2 hours to under 10 minutes. I also used a lock to make sure the program was thread-safe.
- Utilizing various graphs for data exploration. I created a correlation heatmap to isolate the features most correlated with a property's assessment, which helped me determine which kinds of properties to compare assessments with.
- Combining qualitiative research and statistics to answer a guiding question: What is the effect of zoning on a property's assessment?

## If I had more time, I would:

- Analyze how other factors affect a home's assessment, such as proximity to a school or plot size. A lot of older homes in Lexington are more valuable for their plot size, as they are often torn down, rather than valued for the house itself.
- Expand the zoning amendment analysis to include more towns. Many Massachusetts towns, not just Lexington, were required to add zoning for multi-family properties. I hypothesize that urban cities like Brookline and Medford would be more affected than residential communities like Lexington, since multifamily builders are more likely to profit off of that land.

## How to Use the Assessment Comparison Tool:
Clone the repository and navigate to the project directory in your command line.

Install the required python libraries listed in the `requirements.txt` file using:
```
pip install -r requirements.txt
```
Run the program using:
```
python compare_assessments.py
```
The program will prompt you to enter a Lexington street address. Some real addresses you can try:
- 1 Aaron Rd
- 2 Bacon St
- 3 Dudley Rd

A Dash app will be hosted on your local machine, and an address for the server will be provided. Open a web browser and navigate to the address to view the report. [Here is an example report.](https://drive.google.com/file/d/1iagSQqS7lPHBU__Hr9S5rEggr4MWOAqH/view?usp=sharing)
