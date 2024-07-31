#####################################################
############   ENVIRONMENTAL FACTORS I    ##############
 
"""
Here I make a pie chart displaying the most common sea state, weather and glare conditions during the 17 day cruise.
I take the metadata files from the access database containing the lookup data, including:

- lkpSeaState.xlsx
- lkpWeather.xlsx
- lkpGlare.xlsx

The piechart is made using Plotly (https://plotly.com/), which allows you to make interactive plots.
If you hover over each of the pie chart's you will see the description for each of the codes.

"""

# load all of the required modules
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Define file paths using raw string literals
stationary_survey_path = r'data/stationary_platform_data.xlsx'

# Load the stationary survey data
stationary_survey = pd.read_excel(stationary_survey_path)

# load the metadata files for weather, sea state, and glare
sea_state = pd.read_excel('ECSAS_tables\\lkpSeaState.xlsx')
weather = pd.read_excel('ECSAS_tables\\lkpWeather.xlsx')
glare = pd.read_excel('ECSAS_tables\\lkpGlare.xlsx')

# aggregate the most common Weather, SeaState, and Glare codes for the entire trip
weather_counts = stationary_survey['Weather'].value_counts()
sea_state_counts = stationary_survey['SeaState'].value_counts()
glare_counts = stationary_survey['Glare'].value_counts()

# convert to a df for merging
weather_df = pd.DataFrame({'Code': weather_counts.index, 'Count': weather_counts.values})
sea_state_df = pd.DataFrame({'Code': sea_state_counts.index, 'Count': sea_state_counts.values})
glare_df = pd.DataFrame({'Code': glare_counts.index, 'Count': glare_counts.values})

# merge with the metadata to get descriptive labels
weather_df = weather_df.merge(weather, left_on='Code', right_on='Weather', how='left')
sea_state_df = sea_state_df.merge(sea_state, left_on='Code', right_on='SeaState', how='left')
glare_df = glare_df.merge(glare, left_on='Code', right_on='Glare', how='left')

# use this small function to manually adjust the hover text and avoid cutting off any words incorrectly
def format_hover_text(code, count, text, max_length=30):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        # this function avoids any paragraphs in unwanted areas of a sentence
        if len(current_line + word) + 1 > max_length:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    
    if current_line:
        lines.append(current_line)
    
    return f"Code: {code}<br>Count: {count}<br>" + '<br>'.join(lines)

# now you can format the hover text, here I wanted to display the code, count and description of each code in the pop-ups
weather_df['HoverText'] = weather_df.apply(lambda x: format_hover_text(x['Code'], x['Count'], x['WeatherText']), axis=1)

sea_state_df['HoverText'] = sea_state_df.apply(lambda x: format_hover_text(x['Code'], x['Count'], x['SeaStateText']), axis=1)

glare_df['HoverText'] = glare_df.apply(lambda x: format_hover_text(x['Code'], x['Count'], x['GlareText']), axis=1)

# finally, create a subplot figure with three pie charts
fig = make_subplots(rows=1, cols=3, 
                    subplot_titles=('Weather', 'Sea State', 'Glare'), 
                    specs=[[{'type':'pie'}, 
                            {'type':'pie'}, 
                            {'type':'pie'}]])

# add the Pie Chart for:
# 
# Weather:
fig.add_trace(
    go.Pie(
        labels=weather_df['Code'].astype(str),
        values=weather_df['Count'],
        hovertemplate=weather_df['HoverText'] + '<extra></extra>',
        textinfo='label+percent',
        hoverlabel=dict(bgcolor='black', font_color='white')
    ),
    row=1, col=1
)

# Sea State:
fig.add_trace(
    go.Pie(
        labels=sea_state_df['Code'].astype(str),
        values=sea_state_df['Count'],
        hovertemplate=sea_state_df['HoverText'] + '<extra></extra>',
        textinfo='label+percent',
        hoverlabel=dict(bgcolor='black', font_color='white')
    ),
    row=1, col=2
)

# Glare:
fig.add_trace(
    go.Pie(
        labels=glare_df['Code'].astype(str),
        values=glare_df['Count'],
        hovertemplate=glare_df['HoverText'] + '<extra></extra>',
        textinfo='label+percent',
        hoverlabel=dict(bgcolor='black', font_color='white')
    ),
    row=1, col=3
)

# Update the layout to show subplot titles and add a main title with additional text
fig.update_layout(
    showlegend=False,
    title_text="Figure 2. Weather, glare and sea state codes used by the observer most during the cruise period (May 12 - May 29)",
    )

# Save the figure as an HTML file
fig.write_html('figures/pie_charts.html')
