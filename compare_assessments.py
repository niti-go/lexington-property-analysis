import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
#import plotly.graph_objects as go

df = pd.read_csv ("all_data.csv")

#Remove '$' and ',' from current assessment column
df["Current Assessment"] = df["Current Assessment"].str.replace("$","").str.replace(",","")
df["Current Assessment"] = pd.to_numeric(df["Current Assessment"])
df = df.sort_values("Current Assessment")

df["Year Built"] = pd.to_numeric(df["Year Built"])

df["Living Area"] = df["Living Area"].str.replace(",","")
df["Living Area"] = pd.to_numeric(df["Living Area"])

#df containing similar houses
df = df[df["Current Assessment"] <= 4000000]
df = df[df["Year Built"] > 2000]
df = df[df["Living Area"] < 10000]

#dataframe containing similar houses
sim = df
sim=sim[sim["Living Area"]<=4200]
sim=sim[sim["Living Area"]>=4000]
sim=sim[sim["Year Built"]>=2015]

#The house in question
your_loc = "24 PHILIP RD"
df["Highlight"] = df["Location"] == your_loc

#------Scatterplot----------

#Plot all houses
fig=go.Figure(data=go.Scatter3d(x=df["Living Area"], y=df["Year Built"], z=df["Current Assessment"], 
                                mode='markers', marker=dict(
                                       size=10, color=df["Current Assessment"], colorscale='plotly3',
                                       opacity=0.8, reversescale=True),text=df["Location"], name="Other House"))
fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))

# Add the individual house as a green dot
fig.add_trace(go.Scatter3d(
    x=df[df["Highlight"] == True]["Living Area"],
    y=df[df["Highlight"] == True]["Year Built"],
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
fig.show()
#----------Boxplot-------------

plt.figure(figsize=(4, 6))
vals,names,xs = [],[],[]
vals.append(sim["Current Assessment"].values)
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