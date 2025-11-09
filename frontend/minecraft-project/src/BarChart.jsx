import './styles/App.css'
import ReactEcharts from "echarts-for-react"; 
import { useEffect, useState } from 'react';
// x = label, y = val
// props is a json obj

function BarChart({data, onSelect}) {
    const [selected, setSelected] = useState(null);
    const [option, setOption] = useState({});
    const defaultColor = '#5470C6';
    const highlightColor = '#FF5733';
    
    console.log(data)
    useEffect(() => {
        const opt = {
            xAxis: {
                type: 'category',
                data: data && data.length > 0 ? data.map((x) => x[0]) : [],
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
                    data: data && data.length > 0 ? data.map((x) => ({
                        value: x[1],
                        itemStyle: { color: selected === x[0] ? highlightColor : defaultColor }
                    })) : [] ,
                    type: 'bar'
                }
            ]
        }; 
        setOption(opt)
    }, [selected, data])

    const onChartClick = (params) => {
        setSelected(params.name)
        if (onSelect) {
            onSelect(params.name);
        } 
    };

    const onEvents = {
        click: onChartClick,
    };

    return (
        <div style={{width: "100%"}}>
            <ReactEcharts option={option} onEvents={onEvents}/>
        </div>
    )
}
export default BarChart
