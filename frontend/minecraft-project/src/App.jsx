import { useState } from 'react'
import './App.css'
import RankingsContainer from './RankingsContainer';

function App() {
  return (
    <div style={{width:"100vw"}}>
      <h1>Minecraft Data Visualizer</h1>
      <RankingsContainer 
        metric="uptime"
        numRankings={150}
      />
      <RankingsContainer 
        metric="capacity"
        numRankings={150}
      />      
    </div>
  )
}

export default App
