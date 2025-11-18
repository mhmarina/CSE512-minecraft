import './styles/App.css';
import { API_BASE_URL } from './Constants';
import { useEffect, useState } from 'react';
import LineGraph from './LineGraph';
import Select from 'react-select';
import { defaultTheme } from 'react-select';


function SearchContainer({metric, numRankings}) {
    const [rangeUptimeData, setRangeUptimeData] = useState(null)
    const [rangeCapacityData, setRangeCapacityData] = useState(null)
    const [dayUptimeData, setDayUptimeData] = useState(null)
    const [dayCapacityData, setDayCapacityData] = useState(null)
    const [selectedIp, setSelectedIp] = useState(null)
    const [selectedUptimeDay, setSelectedUptimeDay] = useState(null)
    const [selectedCapacityDay, setSelectedCapacityDay] = useState(null)
    const [avgUptime, setAvgUptime] = useState(0)
    const [avgCapacity, setAvgCapacity] = useState(0)
    const [ipList, setIpList] = useState([])

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
                console.log(data)
                setAvgUptime(data)
            }
        }
        async function fetchAvgCapacity(){
            const data = await fetchAvg("capacity")
            if(data){
                console.log(data)
                setAvgCapacity(data)
            }
        }
        fetchUptimeData()
        fetchCapacityData()
        fetchAvgCapacity()
        fetchAvgUptime()
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
        setSelectedIp(option.value[0])
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
        <div styles={{display: "flex", flexDirection: "column", width:"100vw"}}>
            <div style={{ display: "flex", width: "100%", justifyContent: "center"}}>
                <div style={{ width: "50%" }}> {/* wrapper div enforces width */}
                    <Select
                    className="basic-single"
                    classNamePrefix="select"
                    name="Server IPs"
                    options={ipList}
                    styles={{
                            option: (styles) => ({ ...styles, color: "#000" }),
                            control: (styles) => ({ ...styles, width: "100%" }), // fill wrapper
                            menu: (styles) => ({ ...styles, width: "100%" }),    // match wrapper
                        }}
                    onChange={(option)=>onIPSelect(option)}
                    />
                </div>
            </div>
            <div style={{display:"flex", flexDirection:"row"}}>
                ${avgCapacity}
                <LineGraph
                    data={rangeCapacityData}
                    onSelect={onCapacitySelect}
                />
                <LineGraph
                    data={dayCapacityData}
                />
            </div>
            <div style={{display:"flex", flexDirection:"row"}}>
                ${avgUptime}
                <LineGraph
                    data={rangeUptimeData}
                    onSelect={onUptimeSelect}
                />
                <LineGraph
                    data={dayUptimeData}
                />
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