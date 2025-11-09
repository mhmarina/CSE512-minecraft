import './App.css';
import { API_BASE_URL } from './Constants';
import LineGraph from './LineGraph';
import { useEffect, useState } from 'react';

function LineGraphContainer({ selected }) {
    // selected[0] = selectedUptime, selected[1] = selectedCapacity
    const [uptimeData, setUptimeData] = useState(null);
    const [capacityData, setCapacityData] = useState(null);

    useEffect(() => {
        async function fetchUptimeRange() {
            if(!selected[0]) return;
            const url = `${API_BASE_URL}api/uptime/range/${selected[0]}`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                setUptimeData(result);
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
            }
        }
        fetchUptimeRange();
    }, [selected[0]]);

    useEffect(() => {
        async function fetchCapacityRange() {
            if(!selected[1]) return;
            const url = `${API_BASE_URL}api/capacity/range/${selected[1]}`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                console.log(result);
                setCapacityData(result);
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
            }
        }
        fetchCapacityRange();
    }, [selected[1]]);

    return (
        <div style={{display: "flex", flexDirection: "column", width: "50%"}}>
            <div>
                <h2>Capacity for {selected[1]} per day</h2>
                <div>
                    {capacityData && <LineGraph setData={setCapacityData} type="capacity" name={selected[1]} data={capacityData}/>}
                </div>
            </div>
            <div>
                <h2>Uptime for {selected[0]} per day</h2>
                <div>
                    {uptimeData && <LineGraph setData={setUptimeData} type="uptime" name={selected[0]} data={uptimeData}/>}
                </div>
            </div>
        </div>
    );
}

export default LineGraphContainer;