import './App.css'
import ReactEcharts from "echarts-for-react"; 
// x = label, y = val
// props is a json obj

function BarChart(props) {
    console.log(props.data)
    const option = {
        xAxis: {
            type: 'category',
            data: props.data.map((x) => x[0]),
            axisLabel: {
                show: false // hides labels
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
                type: 'bar'
                }
            ]
        }; 

        // todo: use this to visualize a closeup nearby (line graph wtv)
        // maybe change color on click too to freeze selection 
        const onChartClick = (params) => {
        console.log(params.name);
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
