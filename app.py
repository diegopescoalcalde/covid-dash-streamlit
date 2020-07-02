from covidanalysis import ExploratoryAnalysis
import streamlit as st
import pandas as pd
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots



def main():

    st.title('COVID-19 Dashboard')

    df = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv")
    df.date = pd.to_datetime(df['date'])
    # print(df.dtypes)

    try:

        EA = ExploratoryAnalysis(df)

        st.sidebar.title('Options')

        page = st.sidebar.radio("Navigation", ("Introduction", "Graphics", "Analysis"))

        if page == "Analysis":

            st.markdown('The Analysis dashboard presents information in table and writen form, mainly for Data Scientists. '
                        'It allows a better understanding of the data being imported and its metadata. Use the sidebar '
                        'menu to display information.')

            if st.sidebar.checkbox('Dataframe'):
                st.subheader('Dataframe:')
                st.markdown('This section presents the entire dataset with its raw values. It is good in case you need '
                        'to see the overall information available and its format.')
                st.write(df)

            # if st.sidebar.checkbox('Summary (Sum Total)'):
            #     st.subheader('Summary (Sum Total):')
            #     variables = st.multiselect("Choose input variables", df.columns)
            #     total = df[variables].sum()
            #     st.write(total)

            if st.sidebar.checkbox('Statistics (Describe)'):
                st.subheader('Dataframe Description:')
                st.markdown('This section describes basic statistic information from the columns in the dataset. '
                            'Minimum and maximum, mean, standard deviation and quartiles can be checked.')
                st.write(df.describe())

            # if st.sidebar.checkbox('Dataframe Shape'):
            #     st.subheader('Dataframe Shape:')
            #     st.markdown('This is a summary of ')
            #     st.write(df.shape)

            if st.sidebar.checkbox('Info'):
                st.subheader('Dataframe information:')
                st.markdown('This is a summary of the dataset information. It shows how many rows and columns are in'
                            'the file, what is the data type of each variable, name of the columns and how many'
                            'non-null values they have.')
                st.text(EA.info())

            if st.sidebar.checkbox('Missing Values'):
                st.subheader('Missing Values')
                st.markdown('Dealing with missing values is an important pre-processing part that impacts directly'
                            'the results obtained in an analysis. This section allows you to see what is the percentage'
                            'of missing values in each variable to take this into account.')
                st.write((df.isnull().sum() / df.shape[0]).sort_values(ascending=False))



            if st.sidebar.checkbox('Unique values and frequency'):
                st.subheader('Unique values and frequency')
                st.markdown('This part allows you to see what are the unique values that can be found in each column'
                            'of the dataset, and how many times they appear. This is helpful if you need to know '
                            'whether an information is in the dataset, or if you need to compare the frequency of'
                            'different values.')
                col = st.selectbox('Choose a column to see unique values', df.columns)

                st.write(EA.info2(col))



        if page == "Introduction":

            st.markdown('This is a simple dashboard of information about COVID-19 pandemic crisis. It is based on '
                        'information of [Our World In Data](https://ourworldindata.org/), the same source used by '
                        'John Hopkings University.')

            st.markdown('In the Graphics section you will find visual representations of the virus spread and impacts. '
                        'In Analysis section you are able to get information about the imported dataset (this section '
                        'is more useful to Data Scientists).')

            st.markdown(
                'Feel free contact me on [LinkedIn](https://www.linkedin.com/in/diegopesco/) to share your suggestions, '
                'questions or if you need your own custom dashboards.')

        if page == "Graphics":

            st.markdown('Below you can see the total cases per million habitants in the map for a specific date. '
                        'Select countries and charts on the sidebar and click in Plot detailed information to see '
                        'additional information about one or more countries in the bottom of the page. '
                        'You can zoom and hover data in the charts using your mouse.')




            # if st.checkbox('Map'):

            day = pd.to_datetime(st.date_input('Select date'))

            df_map = df[df['date'] == day]

            fig = EA.Map(df_map)

            st.plotly_chart(fig)


            countries = st.sidebar.multiselect('Countries', df.location.unique())

            variable1 = st.sidebar.selectbox('Chart 1', EA.columns)
            variable2 = st.sidebar.selectbox('Chart 2', EA.columns)
            # StartDate = pd.to_datetime(st.date_input('Start Date'))
            # EndDate = pd.to_datetime(st.date_input('End Date'))

            value1 = df.loc[df.location.isin(countries)].population.mean()
            value2 = df.loc[df.location.isin(countries)].population_density.mean()
            value3 = df.loc[df.location.isin(countries)].life_expectancy.mean()
            value4 = df.loc[df.location.isin(countries)].stringency_index.mean()

            if st.sidebar.checkbox('Plot detailed information'):

                if len(countries) == 1:

                    figure = make_subplots(rows=3, cols=1,
                                           row_heights=[0.1, 1, 1],
                                           subplot_titles=("", variable1, variable2),
                                           )


                    plot1 = (EA.LinePlot(countries, variable1))
                    plot2 = (EA.LinePlot(countries, variable2))
                    indicator1, indicator2, indicator3, indicator4 = EA.Indicator(value1, value2, value3, value4)

                    figure.add_trace(plot1, row=2, col=1)
                    figure.add_trace(plot2, row=3, col=1)
                    figure.add_trace(indicator1)
                    figure.add_trace(indicator2)
                    figure.add_trace(indicator3)
                    figure.add_trace(indicator4)

                    figure.update_layout(
                        height=1000,
                        width=700,
                        margin=dict(l=5, r=5, t=5, b=5, pad=0),
                        # title_text="Summary for {}".format(countries),
                        showlegend=False,
                    )

                    st.write(figure)

                else:
                    figure2 = make_subplots(rows=2, cols=2,
                                            specs=[[{}, {}],
                                                   [{"colspan":2}, None]],
                                            row_heights=[1, 1],
                                            subplot_titles=("Population", "Stringency Index", variable1, variable2),
                                            )

                    for cty in countries:

                        plot1 = (EA.LinePlot([cty], variable1))
                        figure2.append_trace(plot1, row=2, col=1)


                        # plot2 = (EA.LinePlot([cty], variable2))
                        # figure2.append_trace(plot2, row=2, col=2)




                    popplot = EA.BarPlot(countries, variable='population')
                    figure2.add_trace(popplot, row=1, col=1)
                    stringencyplot = EA.BarPlot(countries, variable='stringency_index')
                    figure2.add_trace(stringencyplot, row=1, col=2)

                    figure2.update_layout(
                        height=1000,
                        width=700,
                        margin=dict(l=5, r=5, t=20, b=5, pad=0),
                        # title_text="Summary for {}".format(countries),
                        showlegend=True,
                        legend_orientation='h',
                        legend=dict(x=0, y=0.5)
                    )

                    st.write(figure2)

        # if page == "Statistics":
        #     st.subheader('Linear Regression')
        #     Xcolumns = st.multiselect("Choose input variables", EA.columns)
        #     Ycolumn = st.selectbox("Choose response variable", EA.columns)
        #     RegDate = st.date_input('Reg Date')
        #     MissingValues = st.radio("Response Variable Missing values treatment", ("Drop", "Zeros"))
        #     if st.checkbox('Show Results'):
        #         X, Y = EA.PrepRegression(Xcolumns, Ycolumn, MissingValues, RegDate)
        #
        #         DropTerms = st.multiselect("Drop terms", X.columns)
        #
        #         st.text(X)
        #
        #         X, lm = EA.LinearRegression(X, Y, DropTerms)
        #
        #
        #         st.text(lm.summary())





    except Exception as e:
        st.error(e)

if __name__ == '__main__':
    main()