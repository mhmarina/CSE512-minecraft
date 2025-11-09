import './App.css'
import ReactEcharts from "echarts-for-react"; 
import { useState } from 'react';
import { API_BASE_URL } from './Constants';
// x = label, y = val
// props is a json obj

function LineGraph(props) {
    function httpDateToYYYYMMDD(httpDateString) {
        const date = new Date(httpDateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const option = {
        xAxis: {
            type: 'category',
            data: props.data.map((x) => x[0]),
            axisLabel: {
                show: true // hides labels
                }
            },
            dataZoom: [
                {
                    id: 'dataZoomX',
                    type: 'inside',
                    xAxisIndex: [0],
                    filterMode: 'filter'
                },
            ],
            tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            },
            formatter: function (params) {
                const item = params[0];
                return `${item.name}<br/>Value: ${item.value}`;
            }        
        },
        yAxis: {
            type: 'value',
            min: 0,
            max: 1, // slightly above your max value
            interval: 0.5, // controls tick spacing
            axisLabel: {
            formatter: '{value}'
            }   
        },
        series: [
            {
                data: props.data.map((x) => x[1]),
                type: 'line',
                showSymbol: true,
                symbolSize: 8,
                // ensure points are clickable
                emphasis: { focus: 'series' }
            }
            ]
        }; 

        const onChartClick = async (params) => {
            // date: params.name
            // name: data.name
            const url = `${API_BASE_URL}api/${props.type}/day/${props.name}/${httpDateToYYYYMMDD(params.name)}`;
            console.log(url)
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                console.log(result);
                props.setData(result);
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
            }   
        };

        const onEvents = {
            click: onChartClick,
        };

    return (
        <div>
            <ReactEcharts option={option} onEvents={onEvents}/>
        </div>
    )
}
export default LineGraph
