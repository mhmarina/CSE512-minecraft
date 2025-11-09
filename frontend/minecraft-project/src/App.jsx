import { useState } from 'react'
import './App.css'
import BarGraphContainer from './BarGraphContainer'
import LineGraphContainer from './LineGraphContainer'

function App() {
  const [selectedUptime, setSelectedUptime] = useState(null);
  const [selectedCapacity, setSelectedCapacity] = useState(null);

  const handleSelectedUptime = (ip) => {
    setSelectedUptime(ip);
  };

  const handleSelectedCapacity = (ip) => {
    setSelectedCapacity(ip);
  }

  return (
    <div style={{width:"100vw"}}>
      <h1>Minecraft Data Visualizer</h1>
      <div style={{display: 'flex', flexDirection: 'row', gap: '8px'}}>
        <BarGraphContainer onSelect={[handleSelectedUptime, handleSelectedCapacity]} />
        <LineGraphContainer selected={[selectedUptime, selectedCapacity]} />
      </div>
    </div>
  )
}

export default App
