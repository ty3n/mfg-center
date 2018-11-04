# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import datetime
import pandas as pd
import flask
import plotly.plotly as py
from plotly import graph_objs as go
import math
from pymongo import MongoClient
from bson.objectid import ObjectId
from cpk import *

app = dash.Dash()

app.layout = html.Div(
    [
        # header
        html.Div([
            html.Span("D70-MFG Center", className='app-title'),
            # html.Div(
            #     html.Img(src='https://github.com/YenCChien/mfg-center/blob/master/img/logo.png',height="100%")
            #     ,style={"float":"right","height":"100%"})
            ],
            className="row header"
            ),
        # tabs
        html.Div([
            dcc.Tabs(
                id="tabs",
                style={"height":"20","verticalAlign":"middle"},
                children=[
                    dcc.Tab(label="CPK", value="cpk_tab"),
                    dcc.Tab(label="AFI", value="afi_tab"),
                    dcc.Tab(id="cases_tab",label="B", value="b_tab"),
                ],
                value="cpk_tab",
            )
            ],
            className="row tabs_div"
            ),
        
        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),
        html.Link(href="https://use.fontawesome.com/releases/v5.2.0/css/all.css",rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Dosis", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Open+Sans", rel="stylesheet"),
        html.Link(href="https://fonts.googleapis.com/css?family=Ubuntu", rel="stylesheet"),
        html.Link(href="https://cdn.rawgit.com/amadoukane96/8a8cfdac5d2cecad866952c52a70a50e/raw/cd5a9bf0b30856f4fc7e3812162c74bfc0ebe011/dash_crm.css", rel="stylesheet")
    ],
    className="row",
    style={"margin": "0%"},
)



def afiTab():
    return html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=datetime.datetime.now(),
                end_date_placeholder_text='Select a date!'
            ),
            html.Div([
            html.Div(
                [
                    html.P("Leads count per state"),
                    dcc.Graph(
                        id="map",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                    ),
                ],
                className="four columns chart_div"
            ),

            html.Div(
                [
                    html.P("Leads by source"),
                    dcc.Graph(
                        id="lead_source",
                        style={"height": "90%", "width": "98%"},
                        config=dict(displayModeBar=False),
                        figure=dict(data=[go.Pie(
                            labels=['a','b','c','d','e','f'],
                            values=[2,3,5,7,10,8],
                            marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
                            )], layout=dict(margin=dict(l=0, r=0, t=0, b=65), legend=dict(orientation="h")))
                    ),
                ],
                className="four columns chart_div"
            ),
            indicator(
                "#EF553B",
                "Retest Rates",
                "retest_indicator",
            ),
            indicator(
                "#EF553B",
                "PASS Rates",
                "pass_indicator",
            ),
            indicator(
                "#EF553B",
                "FAIL Rates",
                "fail_indicator",
            ),
            ])
        ])

app.config['suppress_callback_exceptions']=True

@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "cpk_tab":
        return cpkTab()
    elif tab == "b_tab":
        return 'No Content'
    elif tab == "afi_tab":
        return afiTab()
    else:
        return opportunities.layout

def parsingRates(cond):
    conn = MongoClient('192.168.12.80:27017')
    db = conn['1521900003T0']
    colls = db.collection_names()
    getPass = 0
    for col in colls:
        if col == 'T1_Log':continue
        collection=eval('db.{}'.format(col))
        getPass += collection.find(cond).count()
    conn.close()
    return getPass

@app.callback(Output("pass_indicator", "children"),
             [Input("date-picker-range", "start_date"),
             Input("date-picker-range", "end_date"),])
def passContent(startDate,endDate):
    if endDate==None:return ''
    stDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    edDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    print(startDate,endDate)
    return parsingRates({'Time':{'$gt': stDate},'Time':{'$lt': edDate},"Result":"PASS"})

@app.callback(Output("fail_indicator", "children"),
             [Input("date-picker-range", "start_date"),
             Input("date-picker-range", "end_date"),])
def failContent(startDate,endDate):
    if endDate==None:return ''
    stDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    edDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    print(startDate,endDate)
    return parsingRates({'Time':{'$gt': stDate},'Time':{'$lt': edDate},"Result":"FAIL"})

@app.callback(Output("retest_indicator", "children"),
             [Input("date-picker-range", "start_date"),
             Input("date-picker-range", "end_date"),])
def nullContent(startDate,endDate):
    if endDate==None:return ''
    stDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    edDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    print(startDate,endDate)
    return parsingRates({'Time':{'$gt': stDate},'Time':{'$lt': edDate},'_id': {'$regex':'-'}})

@app.callback(Output("leads_table", "children"),
             [Input("date-picker", "start_date"),
             Input("date-picker", "end_date"),])
def tables(startDate,endDate):
    if endDate==None:return ''
    stDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    edDate = datetime.datetime.strptime(endDate, "%Y-%m-%d")
    print("---------------",stDate,edDate)
    conn = MongoClient('192.168.12.80:27017')
    db = conn['1521900003T0']
    # colls = db.collection_names()
    collection=db.DsQAM
    getPass = [i for i in collection.find({'Time':{'$gt': stDate,'$lt': edDate},"Result":"PASS"})]
    # print(getPass[0]['Frequency'])
    conn.close()
    df = pd.DataFrame(getPass)
    df = df.drop(['Frequency','ChResult','MeasurePwr','Result','ReportPwr'], axis=1)
    cols = df.columns.tolist()
    colSorted = [cols[-1]]+[cols[-2]]+[cols[-4]]+cols[:-4]
    return df_to_table(df[colSorted].head(3))
    # return df_to_table(df[["_id","Station-id","Time","333000000_R","339000000_R","345000000_R","351000000_R","357000000_R",
    #         "363000000_R","369000000_R","375000000_R","381000000_R","387000000_R","393000000_R","399000000_R","405000000_R",
    #         "411000000_R","417000000_R","423000000_R"]])

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
# Loading screen CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

if __name__ == "__main__":
    app.run_server(debug=True)