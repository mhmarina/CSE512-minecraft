import './App.css';
import { API_BASE_URL } from './Constants';
import BarChart from './BarChart';
import { useEffect, useState } from 'react';

function BarGraphContainer(props) {
    // props.onSelect[0] = handleSelectedUptime, props.onSelect[1] = handleSelectedCapacity
    const [capacityData, setCapacityData] = useState(null);
    const [uptimeData, setUptimeData] = useState(null)

    useEffect(() => {
        async function GetCapacityData() {
            try {
                const resp = await fetch(API_BASE_URL + "api/capacity/10");
                if (!resp.ok) {
                    throw new Error(`Response status: ${resp.status}`);
                }
                const result = await resp.json();
                setCapacityData(result);
            } catch (error) {
                console.error(error.message);
            }
        }
        GetCapacityData();
    }, []);

    useEffect(() => {
    async function GetUptimeData() {
        try {
            const resp = await fetch(API_BASE_URL + "api/uptime/10");
            if (!resp.ok) {
                throw new Error(`Response status: ${resp.status}`);
            }
            const result = await resp.json();
            setUptimeData(result);
            console.log(result)
            } catch (error) {
                console.error(error.message);
            }
        }
        GetUptimeData();
    }, []);

    const handleBarClick = (onSelect, name) => {
        onSelect(name);
    };

    return (
        <div style={{display: "flex", flexDirection: "column", width: "50%"}}>
            <div>
                <h2>Most popular servers</h2>
                <div style={{ display: "flex", flexDirection: "column", alignContent: "center", width: "100%" }}>
                    {capacityData && <BarChart data={capacityData} onBarClick={(name)=>handleBarClick(props.onSelect[1], name)}/>} 
                </div>
            </div>
            <div>
                <h2>Most active servers</h2>
                <div style={{ display: "flex", flexDirection: "column", alignContent: "center", width: "100%"}}>
                    {uptimeData && <BarChart data={uptimeData} onBarClick={(name)=>handleBarClick(props.onSelect[0], name)}/>}
                </div>
            </div>
        </div>
    );
}

export default BarGraphContainer;