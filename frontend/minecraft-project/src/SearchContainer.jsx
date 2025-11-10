import './styles/App.css';
import { API_BASE_URL } from './Constants';
import BarChart from './BarChart';
import { useEffect, useState } from 'react';
import LineGraph from './LineGraph';
import Select from 'react-select';
import { defaultTheme } from 'react-select';


function SearchContainer({metric, numRankings}) {
    const [rangeLineData, setRangeLineData] = useState(null)
    const [dayLineData, setDayLineData] = useState(null)
    const [selectedIp, setSelectedIp] = useState(null)
    const [selectedDay, setSelectedDay] = useState(null)
    const [ipList, setIpList] = useState([])

    useEffect(() => {
        // load list of IPs
        async function fetchListIPs() {
            const url = `${API_BASE_URL}api/ip`;
            try {
                const resp = await fetch(url);
                if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
                const result = await resp.json();
                console.log(result)
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

    // function onLineSelect(day){
    //     setSelectedDay(day)
    // }

    // //get Bar Graph Data
    // useEffect(() => {
    //     async function getBarData() {
    //         try {
    //             const url = API_BASE_URL + `api/${metric}/${numRankings}`
    //             const resp = await fetch(url);
    //             if (!resp.ok) {
    //                 throw new Error(`Response status: ${resp.status}`);
    //             }
    //             const result = await resp.json();
    //             setBarData(result);
    //             } catch (error) {
    //                 console.error(error.message);
    //             }
    //         }
    //     getBarData();
    // }, []);

    // //get selected IP's range data
    // useEffect(() => {
    //     async function fetchRangeData() {
    //         if (selectedIp){
    //             const url = `${API_BASE_URL}api/${metric}/range/${selectedIp}`;
    //             try {
    //                 const resp = await fetch(url);
    //                 if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
    //                 const result = await resp.json();
    //                 setRangeLineData(result);
    //                 // reset selected day
    //                 setSelectedDay(null)
    //             } catch (err) {
    //                 console.error('Failed to fetch range data', err.message);
    //             }
    //         }
    //     }
    //     if(selectedIp){
    //         fetchRangeData();
    //     }
    // }, [selectedIp]);

    // //get selected Day's hourly data
    // useEffect(() => {
    //     async function fetchDayData(){
    //         const url = `${API_BASE_URL}api/${metric}/day/${selectedIp}/${new Date(selectedDay).toISOString().split('T')[0]}`;
    //         try {
    //             const resp = await fetch(url);
    //             if (!resp.ok) throw new Error(`Response status: ${resp.status}`);
    //             const result = await resp.json();
    //             setDayLineData(result);
    //         } catch (err) {
    //             console.error('Failed to fetch range data', err.message);
    //         }  
    //     }
    //     if(selectedIp && selectedDay){
    //         fetchDayData()
    //     }
    //     else if(!selectedDay){
    //         setDayLineData(null)
    //     }
    // }, [selectedDay])


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
                    />
                </div>
            </div>
            <div style={{display:"flex", flexDirection:"row"}}>
                {/* <LineGraph
                    data={rangeLineData}
                />
                <LineGraph
                    data={dayLineData}
                /> */}
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