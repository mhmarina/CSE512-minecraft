import RankingsContainer from './RankingsContainer';
import SearchContainer from './SearchContainer';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';

function App() {
  return (
    <div style={{justifyContent: "center", display: "flex", flexDirection: "column", padding: "50px"}}>
      <h1 style={{fontSize: "4.7em"}}>Minecraft Data Visualizer</h1>
      <div style={{marginBottom: "100px"}}></div>

      <div className="sectionContainer">
        <h2>Top Servers by Uptime</h2>
        <RankingsContainer 
          metric="uptime"
          numRankings={150}
        />
        <h2>Top Servers by Capacity</h2>
        <RankingsContainer 
          metric="capacity"
          numRankings={150}
        />
      </div>

      <div className="sectionContainer">
        <h2>Lookup your Server by IP Address</h2>
        <SearchContainer/>
      </div>

      <div>
        <h2>Definitions</h2>
        <h3>Capacity: number of active users / number of maximum users</h3>
        <h3>Uptime: average time online</h3>
        <a style={{alignSelf: "flex-end"}} target="_blank" href="https://github.com/mhmarina/CSE512-minecraft">       
          <FontAwesomeIcon 
            icon={faGithub}
            style={{fontSize: "25px"}}
          />
        </a>
      </div>
    </div>
  )
}

export default App
