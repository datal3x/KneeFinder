# Knee Finder

A Streamlit web app that identifies the **knee/elbow point** of a curved line using the [kneed](https://github.com/arvkevi/kneed) algorithm.

## What is a Knee Point?

The knee (or elbow) point is the location on a curve where the rate of change shifts significantly - the point of maximum curvature. This is useful for:

- **Clustering**: Finding the optimal number of clusters (elbow method)
- **Thresholds**: Determining cutoff values in data analysis
- **Diminishing returns**: Identifying where adding more resources yields less benefit

## Features

- Upload CSV or TSV files
- Automatic curve detection (concave/convex, increasing/decreasing)
- Adjustable sensitivity parameter
- Interactive Plotly chart with knee point visualization
- Download results as CSV

## Usage

1. Upload your data file (CSV or TSV) or use the sample dataset
2. Select the numeric column to analyze
3. Adjust sensitivity if needed (lower = more aggressive detection)
4. View the knee point on the chart
5. Download results

## Run Locally

```bash
uv run streamlit run app.py
```

## Dependencies

- streamlit
- kneed
- pandas
- plotly
- numpy
- scipy
- millify

## License

MIT
