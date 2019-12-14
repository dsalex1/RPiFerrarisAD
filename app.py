import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import plotly.plotly as py
from plotly.graph_objs import *
from flask import Flask
import numpy as np
import os
import sqlite3
import datetime as dt
import math
import json 
import numpy
import time

app = dash.Dash('streaming-energy-app')
server = app.server

app.layout = html.Div([
    html.Div([
        html.H2("Electricity Consumption"),
        html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png"),
    ], className='banner'),
	html.Div([
		html.Div([
			html.Div([
				html.Div([
					html.H3("Power History (Watt)")
				], className='Title'),
				html.Div([
					dcc.Graph(id='energy-power',className='flexFill'),
				], className='twelve columns energy-power flexFill'),
				dcc.Interval(id='energy-power-update', interval=120000, n_intervals=0),
			], className='row energy-power-row flexFill'),
		], className='nine columns flexFill'),
		html.Div([
		    html.Div([
				html.Div([
					html.H3("Current Power Cons.")
				], className='Title'),
				html.Div([
					html.Div([],className='flexFill'),
					html.Div(
						'XXXX.X'
						,id='cur-pwr',className='number'
					),
					html.Div([],className='flexFill'),
				], className='flexFill')

			], className='row energy-power-row flexFill'),
			html.Div([
				html.Div([
					html.H3("Average Power Cons. (24h)")
				], className='Title'),
				html.Div([
					html.Div([],className='flexFill'),
					html.Div(
						'XXXX.X'
						,id='avg-pwr',className='number'
					),
					html.Div([],className='flexFill'),
				], className='flexFill')
			], className='row energy-power-row flexFill'),
			html.Div([
				html.Div([
					html.H3("Estimated Energy Cons. (1a) ")
				], className='Title'),
				html.Div([
					html.Div([],className='flexFill'),
					html.Div(
						'XXXX.X'
						,id='est-energy',className='number'
					),
					html.Div([],className='flexFill'),
				], className='flexFill')
			], className='row energy-power-row flexFill'),
			html.Div([				
				html.Div([
					html.H3("Maximum / Minimum (24h)")
				], className='Title'),
				html.Div([
					html.Div([],className='flexFill'),
					html.Div(
						'XXXX.X'
						,id='max-min',className='number', style={'font-size': '3rem'}
					),
					html.Div([],className='flexFill'),
				], className='flexFill')
			], className='row energy-power-row flexFill'),
		], className='columns flexFill',style={'width':'500px','flex':'0.3'})
	], className='row',style={'flex':1,'display':'flex'} ),
], className='absoluteCenter flexFill',style={'padding': '0px 10px 15px 10px',
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

		 
 
@app.callback(Output(component_id='cur-pwr', component_property='children'),
              [Input('energy-power', 'figure'),])
def gen_energy_cur_pwr(energy_power_figure):
	energy_val = energy_power_figure['data'][0]
	return str(round(energy_val['y'][-1],1))+"W"

@app.callback(Output(component_id='avg-pwr', component_property='children'),
              [Input('energy-power', 'figure'),])
def gen_energy_avg_val(energy_power_figure):
	energy_val = energy_power_figure['data'][0]
	timestamps=list(map(lambda x:dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp(),energy_val['x']))
	
	firstIncluded=next((x[0] for x in enumerate(timestamps) if x[1] > time.time()-24*60*60),-1)
	timestamps=timestamps[firstIncluded:]
	energy_val['y']=energy_val['y'][firstIncluded:]
	if (len(timestamps)>1):
		return str(round(numpy.trapz(energy_val['y'],timestamps,timestamps[-1])/(timestamps[-1]-timestamps[0]),1))+"W"
	else:
		return str(round(energy_val['y'][0],1))+"W"

@app.callback(Output(component_id='est-energy', component_property='children'),
              [Input('energy-power', 'figure'),])	
def gen_energy_est_energy(energy_power_figure):
	energy_val = energy_power_figure['data'][0]
	
	timestamps=list(map(lambda x:dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp(),energy_val['x']))
	return str(round(numpy.trapz(energy_val['y'],timestamps,timestamps[-1])/(timestamps[-1]-timestamps[0])*8.742,1))+"kWh"

@app.callback(Output(component_id='max-min', component_property='children'),
              [Input('energy-power', 'figure'),])
def gen_energy_max_min(energy_power_figure):
	energy_val = energy_power_figure['data'][0]
	timestamps=list(map(lambda x:dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp(),energy_val['x']))
	
	firstIncluded=next((x[0] for x in enumerate(timestamps) if x[1] > time.time()-24*60*60),-1)
	energy_val['y']=energy_val['y'][firstIncluded:]

	return str(round(max(energy_val['y']),1))+"W / "+str(round(min(energy_val['y']),1))+"W"

		
@app.callback(Output('energy-power', 'figure'), [Input('energy-power-update', 'n_intervals')])
def gen_energy_power(interval):
    
    
    con = sqlite3.connect("./Data/power-data.db")
    c=con.cursor()
    c.execute('SELECT time,power from Power LIMIT 10')
    data=c.fetchall()
    df={}
    df['time']=list(map(lambda x: x[0],data))
    df['power']=list(map(lambda x: x[1],data))

    trace = Scatter(
        y=df['power'],
		x=list(map(lambda x:dt.datetime.utcfromtimestamp(x),df['time'])),
        line=Line(
            color='#42C4F7'
        ),
        mode='lines+markers'
    )

    layout = Layout(
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title='Time Elapsed (sec)'
        ),
        yaxis=dict(

        ),
        margin=Margin(
            t=45,
            l=50,
            r=50
        )
    )

    return Figure(data=[trace], layout=layout)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "C:\\Users\\dsale\\workspace\\enegry dashboard\\dash-wind-streaming\\css\\dash-energy-streaming.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
