import geopandas as gpd
import plotly.express as px


def map_view(df):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    fig = px.scatter_geo(
        gdf,
        hover_data=["city", "purchasing_power", "company_name", "job_title"],
        lat="latitude",
        lon="longitude",
        size="purchasing_power",
        geojson="geometry",
        projection="natural earth",
    )
    fig.show()
    return
