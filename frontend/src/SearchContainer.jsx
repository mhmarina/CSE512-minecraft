import './styles/styles.css'
import { API_BASE_URL } from './Constants';
import { useEffect, useState } from 'react';
import LineGraph from './LineGraph';
import AsyncSelect from 'react-select/async';
import { defaultTheme } from 'react-select';


function SearchContainer() {
    const [rangeUptimeData, setRangeUptimeData] = useState(null)
    const [rangeCapacityData, setRangeCapacityData] = useState(null)
    const [dayUptimeData, setDayUptimeData] = useState(null)
    const [dayCapacityData, setDayCapacityData] = useState(null)
    const [selectedIp, setSelectedIp] = useState(null)
    const [selectedUptimeDay, setSelectedUptimeDay] = useState(null)
    const [selectedCapacityDay, setSelectedCapacityDay] = useState(null)
    const [avgUptime, setAvgUptime] = useState("0.0000")
    const [avgCapacity, setAvgCapacity] = useState("0.0000")
    const [ipList, setIpList] = useState([])

    function loadOptions(inputValue, callback) {
        console.log(inputValue)
        const filtered = ipList
            .filter(ip => ip.label[0].toLowerCase().includes(inputValue.toLowerCase()))
            .slice(0, 50); 
        callback(filtered);
    }

    useEffect(() => {
        // load list of IPs
        async function fetchListIPs() {
            const url = `${API_BASE_URL}api/ip`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                setIpList(result.map((x)=>({
                    value: x,
                    label: x
                })));
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
            }
        }
        fetchListIPs()
    }, [])

    async function fetchRangeData(metric) {
        if (selectedIp){
            const url = `${API_BASE_URL}api/${metric}/range/${selectedIp}`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                return result
            } catch (err) {
                console.error('Failed to fetch range data', err.message);
                return null
            }
        }
    }

    async function fetchDayData(metric, selectedDay){
        const url = `${API_BASE_URL}api/${metric}/day/${selectedIp}/${new Date(selectedDay).toISOString().split('T')[0]}`;
        try {
            const resp = await fetch(url);
            if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
            const result = await resp.json();
            return result;
        } catch (err) {
            console.error('Failed to fetch range data', err.message);
            return null
        }  
    }

    async function fetchAvg(metric){
        const url = `${API_BASE_URL}api/${metric}/avg/${selectedIp}`
        try{
            const resp = await fetch(url)
            if(!resp.ok) throw new Error(`Error fetch avg ${metric} for ${selectedIp}: ${resp.status}`)
            const result = await resp.json();
            return result;
        }catch (err) {
            console.error('Failed to fetch average', err.message);
            return null
        }  
    }

    useEffect(() => {
        async function fetchUptimeData() {
            const data = await fetchRangeData("uptime")
            if(data){
                setRangeUptimeData(data)
                setSelectedUptimeDay(null)
            }
        }
        async function fetchCapacityData() {
            const data = await fetchRangeData("capacity")
            if(data){
                setRangeCapacityData(data)
                setSelectedCapacityDay(null)
            }
        }
        async function fetchAvgUptime(){
            const data = await fetchAvg("uptime")
            if(data){
                setAvgUptime(parseFloat(data).toFixed(4))
            }
        }
        async function fetchAvgCapacity(){
            const data = await fetchAvg("capacity")
            if(data){
                setAvgCapacity(parseFloat(data).toFixed(4))
            }
        }
        if(selectedIp){
            fetchUptimeData()
            fetchCapacityData()
            fetchAvgCapacity()
            fetchAvgUptime()
        }
    }, [selectedIp]);

    useEffect(() => {
        async function fetchData() {
            const data = await fetchDayData("capacity", selectedCapacityDay)
            if(data){
                setDayCapacityData(data)
            }
        }
        if(selectedCapacityDay != null){
            fetchData()
        }
    }, [selectedCapacityDay])

    useEffect(() => {
        async function fetchData() {
            const data = await fetchDayData("uptime", selectedUptimeDay)
            if(data){
                setDayUptimeData(data) 
            }
        }
        if(selectedUptimeDay != null){
            fetchData()
        }
    }, [selectedUptimeDay])

    function onIPSelect(option){
        setSelectedIp(option.value)
        setDayCapacityData(null)
        setDayUptimeData(null)
    }

    function onCapacitySelect(day){
        setSelectedCapacityDay(day)
    }

    function onUptimeSelect(day){
        setSelectedUptimeDay(day)
    }

    return (
        <div style={{display: "flex", flexDirection: "column", overflow: "hidden"}}>
            <div style={{ display: "flex", justifyContent: "center"}}>
                <div style={{ width:"50%"}}>
                <AsyncSelect
                    cacheOptions
                    loadOptions={loadOptions}
                    defaultOptions={ipList.slice(0, 50)} 
                    onChange={onIPSelect}
                    styles={{
                        option: (styles) => ({ ...styles, color: "#000" }),
                        control: (styles) => ({ ...styles, width: "100%" }),
                        menu: (styles) => ({ ...styles, width: "100%" }),
                    }}
                />
                </div>
            </div>
            <div className='graphContainer'>
                <div className='aggregateDiv'>
                    <h3>Average Capacity</h3>
                    <h1>{avgCapacity}</h1>
                </div>
                <div>
                    <LineGraph
                        data={rangeCapacityData}
                        onSelect={onCapacitySelect}
                    />
                </div>
                <div>
                    <LineGraph
                        data={dayCapacityData}
                    />
                </div>
            </div>
            <div className='graphContainer'>
                <div className='aggregateDiv'>
                    <h3>Average Uptime</h3>
                    <h1>{avgUptime}</h1>
                </div>
                <div>
                    <LineGraph
                        data={rangeUptimeData}
                        onSelect={onUptimeSelect}
                    />
                </div>
                <div>
                    <LineGraph
                        data={dayUptimeData}
                    />
                </div>
            </div>
        </div>
    );
}

// cheatsheet for Select
// control	The main select box (the visible input field)	Width, height, border, background
// menu	The dropdown menu that appears when you click	Can override width, background, box shadow
// menuList	The scrollable list inside the menu	Can set padding, max height, overflow
// option	Each option inside the menu	Styling for hover, selected, disabled, color, etc.
// placeholder	Placeholder text inside the input box	Color, font, etc.
// singleValue	The selected value when not multi-select	Font, color, alignment
// multiValue	Each selected item in multi-select mode	Background, border, padding
// multiValueLabel	Text inside a multi-select item	Font, color
// multiValueRemove	The “x” button inside a multi-select item	Color, hover color, cursor
// indicatorSeparator	Small separator before dropdown arrow	Usually remove with display: 'none'
// dropdownIndicator	The arrow icon	Color, rotation, padding

export default SearchContainer;