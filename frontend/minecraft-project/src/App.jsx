import './styles/App.css'
import RankingsContainer from './RankingsContainer';

function App() {
  return (
    <div style={{width:"100vw"}}>
      <h1>Minecraft Data Visualizer</h1>
      <RankingsContainer 
        metric="uptime"
        numRankings={2}
      />
      <RankingsContainer 
        metric="capacity"
        numRankings={2}
      />      
    </div>
  )
}

export default App
