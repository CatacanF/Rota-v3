import plotly.graph_objects as go
import json

# Load the data
data = {
    "categories": ["Success Rate", "Response Time (sec)", "Rate Limit Errors", "Cache Hit Rate (%)", "API Calls/Min"],
    "before": [70, 2.5, 25, 0, 100],
    "after": [100, 0.15, 0, 90, 10]
}

# Abbreviate categories to fit 15 character limit
abbreviated_categories = [
    "Success Rate",
    "Response (sec)",
    "Rate Errors",
    "Cache Hit (%)",
    "API Calls/Min"
]

# Create grouped bar chart
fig = go.Figure()

# Add Before Rate Limiter bars
fig.add_trace(go.Bar(
    name='Before',
    x=abbreviated_categories,
    y=data['before'],
    marker_color='#1FB8CD',
    text=data['before'],
    textposition='auto',
    cliponaxis=False
))

# Add After Rate Limiter bars
fig.add_trace(go.Bar(
    name='After',
    x=abbreviated_categories,
    y=data['after'],
    marker_color='#2E8B57',
    text=data['after'],
    textposition='auto',
    cliponaxis=False
))

# Update layout
fig.update_layout(
    title='Rate Limiter Performance Comparison',
    xaxis_title='Metrics',
    yaxis_title='Value',
    barmode='group',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5
    )
)

fig.update_traces(cliponaxis=False)

# Save as both PNG and SVG
fig.write_image('rate_limiter_comparison.png')
fig.write_image('rate_limiter_comparison.svg', format='svg')

print("Charts saved: rate_limiter_comparison.png and rate_limiter_comparison.svg")
