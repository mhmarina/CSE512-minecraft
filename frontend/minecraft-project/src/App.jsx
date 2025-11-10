import './styles/App.css'
import RankingsContainer from './RankingsContainer';
import SearchContainer from './SearchContainer';

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
      <SearchContainer/>
    </div>
  )
}

export default App
