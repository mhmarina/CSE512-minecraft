import './App.css';
import { API_BASE__URL } from './Constants';
import BarChart from './BarChart';
import { useEffect, useState } from 'react';

function GraphContainer(props) {
    const [capacityData, setCapacityData] = useState(null);
    const [uptimeData, setUptimeData] = useState(null)

    useEffect(() => {
        async function GetCapacityData() {
            try {
                const resp = await fetch(API_BASE__URL + "api/capacity/150");
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
            const resp = await fetch(API_BASE__URL + "api/uptime/2000");
            if (!resp.ok) {
                throw new Error(`Response status: ${resp.status}`);
            }
            const result = await resp.json();
            setUptimeData(result);
            } catch (error) {
                console.error(error.message);
            }
        }
        GetUptimeData();
    }, []);

    return (
        <div style={{display: "flex", flexDirection: "column"}}>
            <div>
                <h2>Most popular servers</h2>
                <p>Ranks servers based on average number of players/ maximum number of players</p>
                <div style={{ display: "flex", flexDirection: "column", alignContent: "center", width: "90vw" }}>
                    {capacityData && <BarChart data={capacityData}/>}
                </div>
            </div>
            <div>
                <h2>Most active servers</h2>
                <p>Ranks servers based on average uptime (onlineness)</p>
                <div style={{ display: "flex", flexDirection: "column", alignContent: "center", width: "90vw"}}>
                    {uptimeData && <BarChart data={uptimeData}/>}
                </div>
            </div>
        </div>
    );
}

export default GraphContainer;