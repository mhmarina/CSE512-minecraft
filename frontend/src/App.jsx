import RankingsContainer from './RankingsContainer';
import SearchContainer from './SearchContainer';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGithub } from '@fortawesome/free-brands-svg-icons';

function App() {
  return (
    <div style={{justifyContent: "center", display: "flex", flexDirection: "column"}}>
      <a style={{alignSelf: "flex-start"}} target="_blank" href="https://github.com/mhmarina/CSE512-minecraft">       
        <FontAwesomeIcon 
          icon={faGithub}
          style={{fontSize: "25px"}}
        />
      </a>
      <h1>Minecraft Data Visualizer</h1>
      <div style={{marginBottom: "100px"}}></div>
      <h2>Top Servers by Uptime</h2>
      <RankingsContainer 
        metric="uptime"
        numRankings={1}
      />
      <h2>Top Servers by Capacity</h2>
      <RankingsContainer 
        metric="capacity"
        numRankings={1}
      />
      <div style={{marginBottom: "100px"}}></div>
      <h2 style={{marginBottom: "50px"}}>Lookup your Server by IP Address</h2>
      <SearchContainer/>
      <div style={{marginBottom: "100px"}}></div>
      <div style={{textAlign: 'left', display: "flex", alignSelf: "center", justifySelf: "center"}}>
        <h2>Definitions</h2>
        <ul>
          <li>Capacity: number of active users / number of maximum users</li>
          <li>Uptime: average time online</li>
        </ul>
      </div>
    </div>
  )
}

export default App
