import './App.css'
import ReactEcharts from "echarts-for-react"; 
import { useEffect, useState } from 'react';
// x = label, y = val
// props is a json obj

function BarChart(props) {
    const [option, setOption] = useState({});
    const [selected, setSelected] = useState(null);
    const defaultColor = '#5470C6';
    const highlightColor = '#FF5733';

    useEffect(() => {
        const opt = {
            xAxis: {
                type: 'category',
                data: props.data.map((x) => x[0]),
                axisLabel: {
                    show: false
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
                max: 1,
                interval: 0.5,
                axisLabel: {
                formatter: '{value}'
                }   
            },
            series: [
                {
                    data: props.data.map((x) => ({
                        value: x[1],
                        itemStyle: { color: selected === x[0] ? highlightColor : defaultColor }
                    })),
                    type: 'bar'
                }
            ]
        }; 
        setOption(opt)
    }, [selected])

        const onChartClick = (params) => {
            setSelected(params.name)
            if (props.onBarClick) {
                props.onBarClick(params.name);
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
export default BarChart
