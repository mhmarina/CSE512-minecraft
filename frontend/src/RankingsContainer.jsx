import './styles/styles.css'
import { API_BASE_URL } from './Constants';
import BarChart from './BarChart';
import { useEffect, useState } from 'react';
import LineGraph from './LineGraph';

function RankingsContainer({metric, numRankings}) {
    const [barData, setBarData] = useState(null)
    const [rangeLineData, setRangeLineData] = useState(null)
    const [dayLineData, setDayLineData] = useState(null)
    const [selectedIp, setSelectedIp] = useState(null)
    const [selectedDay, setSelectedDay] = useState(null)

    function onBarSelect(ip){
        setSelectedIp(ip)
    }

    function onLineSelect(day){
        setSelectedDay(day)
    }

    //get Bar Graph Data
    useEffect(() => {
        async function getBarData() {
            try {
                const url = API_BASE_URL + `api/${metric}/${numRankings}`
                const resp = await fetch(url);
                if (!resp.ok) {
                    throw new Error(`Response status: ${resp.status}`);
                }
                const result = await resp.json();
                setBarData(result);
                } catch (error) {
                    console.error(error.message);
                }
            }
        getBarData();
    }, []);

    //get selected IP's range data
    useEffect(() => {
        async function fetchRangeData() {
            if (selectedIp){
                const url = `${API_BASE_URL}api/${metric}/range/${selectedIp}`;
                try {
                    const resp = await fetch(url);
                    if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                    const result = await resp.json();
                    setRangeLineData(result);
                    // reset selected day
                    setSelectedDay(null)
                } catch (err) {
                    console.error('Failed to fetch range data', err.message);
                }
            }
        }
        if(selectedIp){
            fetchRangeData();
        }
    }, [selectedIp]);

    //get selected Day's hourly data
    useEffect(() => {
        async function fetchDayData(){
            const url = `${API_BASE_URL}api/${metric}/day/${selectedIp}/${new Date(selectedDay).toISOString().split('T')[0]}`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                setDayLineData(result);
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
            }  
        }
        if(selectedIp && selectedDay){
            fetchDayData()
        }
        else if(!selectedDay){
            setDayLineData(null)
        }
    }, [selectedDay])


    return (
        <div className='graphContainer'>
            <div style={{alignSelf: "flex-end"}}>
                <BarChart
                    onSelect={onBarSelect}
                    data={barData}
                />
            </div>
            <div style={{alignSelf: "flex-end"}}>
                <h3>{selectedIp ? "selected server: " + selectedIp : "select a server for daily stats"}</h3>
                <LineGraph
                    onSelect={onLineSelect}
                    data={rangeLineData}
                />
            </div>
            <div style={{alignSelf: "flex-end"}}>
                <h3>{selectedDay ? "selected day: " + selectedDay : "select a day for hourly stats"}</h3>
                <LineGraph
                    data={dayLineData}
                />
            </div>
        </div>
    );
}

export default RankingsContainer;