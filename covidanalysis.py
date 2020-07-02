import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import io
import streamlit as st
import random
import numpy as np
import plotly as py
from plotly.offline import iplot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px


# Exploratory Analysis Class
class ExploratoryAnalysis:

    def __init__(self, dataframe):
        self.df = dataframe
        self.columns = dataframe.columns
        self.numerical_columns = [name for name in self.columns if
                                  (self.df[name].dtype == 'int64') | (self.df[name].dtype == 'float64')]

    def info(self):
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        return buffer.getvalue()

    def info2(self, column_target):
        df = self.df[column_target].value_counts().to_frame().reset_index()
        df.sort_values(by='index', inplace=True, ignore_index=True)
        df.rename(columns={'index': column_target, '{}'.format(column_target): "Values Frequency"}, inplace=True)
        return df

    def CountPlot(self, column_target, hue=None):
        sns.set(style="darkgrid")
        return sns.countplot(x=column_target, data=self.df, hue=hue, palette='pastel')

    def HeatMapCorr(self):
        sns.set(style="darkgrid")
        sns.set(font_scale=0.6)
        corr = self.df.corr()
        return sns.heatmap(corr, annot=True, annot_kws={"size": 7}, linewidths=.5)

    def DistPlot(self, column_target):
        sns.set(style="darkgrid")
        return sns.distplot(self.df[column_target], color='c')

    def PairPlot(self, hue=None):
        sns.set(style="darkgrid")
        return sns.pairplot(self.df, hue=hue, palette="coolwarm")

    def BoxPlot(self, column_x=None, column_y=None, hue=None):
        sns.set(style="darkgrid")
        return sns.boxplot(x=column_x, y=column_y, hue=hue, data=self.df, palette="Set3")

#Pre-processing Data

    def Filter(self, GroupBy, FilterVariable, MinimumValue):
        #Group rows by a subgroup and find groups that have a minimum value
        df_ref = self.df.groupby(GroupBy).sum() > MinimumValue
        df_ref = df_ref[df_ref[FilterVariable] == True].index

        #Create a DataFrame only with rows of these groups
        df_filter = self.df[self.df[GroupBy].isin(df_ref)]
        return df_filter

#Statistical Analysis

    def PrepRegression(self, Xcolumns, Ycolumn, MissingValues, RegDate):

        if (MissingValues == "Zeros"):
            self.df[Ycolumn].fillna(0, inplace=True)
        else:
            self.df.dropna(subset=[Ycolumn],inplace=True)
        # self.df.dropna(inplace=True)
        # self.df['data'] = pd.to_datetime(self.df.date)
        time_x = self.df[self.df['date'] == str(RegDate)]
        time_x.dropna(subset=Xcolumns, inplace=True)
        # time_x = time_x[Xcolumns, Ycolumn]
        X = time_x[Xcolumns]
        # X = pd.get_dummies(self.df[Xcolumns])
        Y = time_x[Ycolumn]

        return X, Y

    def LinearRegression(self, X, Y, DropTerms):
        #if DropTerms !=0:
        X.drop(DropTerms, axis=1, inplace=True)

        lm = sm.OLS(Y, sm.add_constant(X)).fit()

        return X, lm

    def ParetoPlot(self, X, lm):
        coefs = lm.params.drop('const')
        pareto = 2 * (coefs)
        pareto = pd.DataFrame(pareto)
        pareto.columns = ['Effect']
        pareto.sort_values(by='Effect', ascending=True, inplace=True)

        #return pareto
        return sns.barplot(x="Effect", y=pareto.index, data=pareto)


    def LinePlot(self, countries, variable):
        x = self.df.loc[self.df.location.isin(countries)]
        # time_x = x.loc[x.date >= StartDate]
        # time_x = time_x.loc[time_x.date <= EndDate]

        trace = go.Scatter(
            x=x["date"],
            y=x[variable],
            mode='lines',
            name=str(countries)
        )

        return trace

    def BarPlot(self, countries, variable):
        x = self.df.loc[self.df.location.isin(countries)]
        x = x.groupby(['location']).mean()

        trace = go.Bar(
            x=x.index,
            y=x[variable],
            name=str(countries),
            showlegend=False
        )
        return trace

    def Indicator(self, value1, value2, value3, value4):
        indicator1 = go.Indicator(
            mode='number',
            value=value1,
            number = dict(font = dict(size=40)
            ),
            domain={'x':[0, 0.25], 'y':[0.85, 1]},
            title = dict(text='Population',
                         font=dict(size=20))
        )

        indicator2 = go.Indicator(
            mode='number',
            value=value2,
            number = dict(font = dict(size=40)
            ),
            domain={'x':[0.25, 0.5], 'y':[0.85, 1]},
            title=dict(text='Pop. Density',
                       font=dict(size=20))
        )

        indicator3 = go.Indicator(
            mode='number',
            value=value3,
            number = dict(font = dict(size=40)
            ),
            domain={'x':[0.5, 0.75], 'y':[0.85, 1]},
            title=dict(text='Life Exp.',
                       font=dict(size=20))
        )

        indicator4 = go.Indicator(
            mode='number',
            value=value4,
            number = dict(font = dict(size=40)
            ),
            domain={'x':[0.75, 1], 'y':[0.85, 1]},
            title=dict(text='Stringency Index',
                       font=dict(size=20))
        )

        return indicator1, indicator2, indicator3, indicator4

    def Map(self, df_map):

        data = go.Choropleth(
            locations=df_map['iso_code'],
            z=df_map['total_cases_per_million'],
            text=df_map['location'],
            colorscale='Reds',
            autocolorscale=True,
            reversescale=False,
            zauto=False,
            zmin=0,
            zmax=10000
            # marker_line_color='darkgray',
            # marker_line_width=0.5,
            # colorbar_tickprefix='$',
            # colorbar_title=dict('GDP<br>Billions US$')
        )

        fig = go.Figure(data)
        fig.update_layout(
            title_text='Total cases of COVID-19 per million habitants',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular',
            ),
            margin = dict(l=5, r=5, t=70, b=5, pad=10)
        )


        return fig