import json
from config import *

template = '''
    <h2 class="text-center" style="padding-top: 40px">{full_name}</h2>
    <div id="chart_container_{name}" class="row">
        <div class="col-sm-10">
            <div id="chart_{name}"></div>
        </div>
        <div id="legend_container_{name}">
            <div id="smoother_{name}" title="Smoothing"></div>
            <div id="legend_{name}"></div>
        </div>
        <div id="slider_{name}"></div>
    </div>
     
    <script> 
     
    var graph = new Rickshaw.Graph( {
        element: document.querySelector("#chart_{name}"), 
        renderer: 'line',
        series: {series}
    });
     
    graph.render();
    var hoverDetail = new Rickshaw.Graph.HoverDetail( {
        graph: graph
    } );

    var legend = new Rickshaw.Graph.Legend( {
        graph: graph,
        element: document.getElementById('legend_{name}')

    } );

    var shelving = new Rickshaw.Graph.Behavior.Series.Toggle( {
        graph: graph,
        legend: legend
    } );

    var axes = new Rickshaw.Graph.Axis.Time( {
        graph: graph
    } );
    axes.render();
     
    </script> 
'''

def render_graph(name, full_name, input_series, series_names):
    output = template

    series = []
    for i, input_serie in enumerate(input_series):
        data = [{'x': x, 'y': y} for x,y in input_serie]
        series.append({'color': colors[i], 'data': data, 'name': series_names[i]})
        

    context = {
        'name': name,
        'full_name': full_name,
        'series': json.dumps(series),
        }

    for key, value in context.items():
        output = output.replace('{'+key+'}', value)

    return output
