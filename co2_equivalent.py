
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import pycountry_convert as pc
import pydeck as pdk


@st.cache

def country_to_continent(country_name):
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name

def load_data():
    #load the emissions data
    df_emissions = pd.read_excel('CO2_historical_country.xlsx',skiprows=1, )
    df_emissions=df_emissions.rename(columns={"Unnamed: 0":"Year"})
    df_emissions=df_emissions.melt(id_vars="Year", var_name="Country", value_name="Emissions")
    df_emissions["Country"]=df_emissions["Country"].replace( 'United States of America', 'United States' )

    #load GDP data
    gdp=pd.read_excel("GDP.xlsx",skiprows=3)
    gdp=gdp.rename(columns={"Country Name":"Country"})
    gdp2=gdp.drop(columns=["Country Code","Indicator Name","Indicator Code"]).melt(id_vars="Country", var_name="Year", value_name="gdp")
    gdp2["Year"]=gdp2["Year"].astype("int64")

    #merge
    df_merge=df_emissions.merge(gdp2, how="outer", on=["Year", "Country"])

    return df_merge

def main():

    data = load_data()
    data["Emissions_round"]=data["Emissions"].apply(np.ceil)
    data=data.sort_values(by="Year")
    data=data.dropna()
    drop_list=['Timor-Leste','Kosovo']
    data=data[~data["Country"].isin(drop_list)]
    data["Continent"]=data["Country"].apply(country_to_continent)

    st.title('CO2 Emissions Worlwide')

    st.header('Worlide Accumulated CO2 Emissions in MtCO₂')
    fig1 = px.icicle(data, path=[px.Constant('world'), 'Continent', 'Country'], values='Emissions',
                    color_discrete_sequence= px.colors.sequential.Viridis
                    #color='lifeExp', hover_data=['iso_alpha']
                    )
    st.plotly_chart(fig1)

    st.header('Yearly CO2 Emissions in MtCO₂ 1960 - 2021 Animation')
    fig2=px.scatter(data, x="gdp",y="Emissions", animation_frame="Year",  animation_group="Country", size="Emissions_round", 
                    size_max=50, range_y=[0,11000],hover_name="Country",color="Continent",
                    color_discrete_sequence= px.colors.sequential.Viridis       
                     )
    fig2.update_layout(
                        xaxis_range=[0,24000000000000]
                        ,xaxis_title="GDP"
                        ,yaxis_title="MtCO₂"
        )
    #log_y=True,
    st.plotly_chart(fig2)

    st.header('Yearly CO2 Emissions in MtCO₂ 1960 - 2021 by Country / Continent')
    df_pivot=data.sort_values(by="Year").set_index("Year")
    df_pivot=pd.pivot_table(df_pivot, columns=["Continent"], index="Year", values="Emissions", fill_value=0, aggfunc=np.sum).reset_index()
    df_pivot_cumsum = df_pivot.copy()

    df_pivot_cumsum.iloc[:,1:]=df_pivot_cumsum.iloc[:,1:].cumsum()
    #fig3, ax = plt.subplots()
    #ax.stackplot(df_pivot["Year"], df_pivot["Africa"],df_pivot["Asia"],df_pivot["North America"],df_pivot["Europe"],df_pivot["Oceania"],df_pivot["South America"])
    #st.plotly_chart(fig3)
    #fig3=plt.stackplot(df_pivot["Year"], df_pivot["Africa"],df_pivot["Asia"],df_pivot["North America"],df_pivot["Europe"],df_pivot["Oceania"],df_pivot["South America"])
    #st.plotly_chart(fig3)
    fig3 = px.area(data, x="Year", y="Emissions", color="Continent", line_group="Country",
                    color_discrete_sequence= px.colors.sequential.Viridis   #Cividis_r #Plasma_r
                    #color_continuous_scale=px.colors.sequential.Cividis_r
                    )
    st.plotly_chart(fig3)

    st.header('Accumulated CO2 Emissions in MtCO₂ 1960 - 2021 by Continent')
    fig4 = px.area(    df_pivot_cumsum, x="Year",
        y=["Asia","Africa", "Europe",	"North America",	"Oceania",	"South America"],
        color_discrete_sequence= px.colors.sequential.Viridis,
    #color="Continent",
    #title="Distribution of daily trading volume - 2017",
    )
    #fig3.update_layout(yaxis_tickformat="%")
    st.plotly_chart(fig4)




    df_21=data[data["Year"]==2021]
    df_21=df_21.sort_values(by="Emissions", ascending=False)


    st.title("CO2 emissions by country")
    #st.sidebar.title("CO2 emissions by country")
    st.markdown("Select a country to see its CO2 emissions")
    #country = st.sidebar.selectbox("Select a country", data["Country"].unique())
    country = st.selectbox("Select a country", data.sort_values(by="Country")["Country"].unique())

    data_country = data[data["Country"] == country]
    st.line_chart(data=data_country, x="Year",y="Emissions")


    # Create a bar chart

    st.title('CO2 Emissions for Year 2021')

    df_21_filt=df_21.head(10)
    fig, ax = plt.subplots()
    ax.bar(df_21_filt['Country'], df_21_filt['Emissions'])
    plt.xlabel('Country')
    plt.ylabel('CO2 Equivalents (million metric tons)')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)





    chart_data = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=['lat', 'lon'])

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-122.4,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
            'HexagonLayer',
            data=chart_data,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=chart_data,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))



if __name__ == "__main__":
    main()












st.title('Industrial CO2 Emissions')

st.write('The following table shows CO2 equivalents produced by different industries.')

#st.table(data)

st.title('Industrial CO2 Emissions by Country')

st.write('The following bar chart shows CO2 equivalents produced by different countries.')

