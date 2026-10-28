import React, {useEffect,useMemo,useState} from 'react'
import {createRoot} from 'react-dom/client'
import {Activity,AlertTriangle,ArrowUpRight,Bell,Database,Download,Layers3,Search,ShieldCheck,Timer,Workflow} from 'lucide-react'
import {Area,AreaChart,Bar,BarChart,CartesianGrid,ResponsiveContainer,Tooltip,XAxis,YAxis} from 'recharts'
import {demoFixtures,summarize,trending} from './demo'
import './styles.css'

const count = (n,decimals=1) => n===null||n===undefined?'—':Number(n).toLocaleString(undefined,{maximumFractionDigits:decimals})
function saveCSV(rows) {
  const fields=['event_id','timestamp','service','score','severity','status','reason','e2e_latency_ms']
  const quote = v=>'"'+String(v??'').replaceAll('"','""')+'"'
  const csv=[fields.join(','),...rows.map(row=>fields.map(f=>quote(row[f])).join(','))].join('\n')
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}))
  const a=document.createElement('a')
  a.href=url;a.download='streamwatch-alerts.csv';a.click()
  URL.revokeObjectURL(url)
}
function App() {
  const [mode,setMode]=useState('live')
  const [live,setLive]=useState({items:[],trends:[],summary:null})
  const [fixtures,setFixtures]=useState(()=>demoFixtures())
  const [error,setError]=useState('')
  const [last,setLast]=useState('')
  const [filter,setFilter]=useState('open')
  const [service,setService]=useState('all')
  const [term,setTerm]=useState('')
  const [token,setToken]=useState('')
  const [busy,setBusy]=useState('')
  useEffect(()=>{
    if(mode!=='live')return
    let cancelled=false
    async function refresh() {
      try {
        const paths=['/api/summary?minutes=60','/api/events?limit=500','/api/trends?minutes=60']
        const responses=await Promise.all(paths.map(p=>fetch(p,{cache:'no-store'})))
        if(responses.some(r=>!r.ok))throw Error('API request failed')
        const [summary,events,trends]=await Promise.all(responses.map(r=>r.json()))
        if(!cancelled){setLive({summary,items:events.items,trends:trends.items});setError('');setLast(new Date().toLocaleTimeString())}
      } catch(e){if(!cancelled)setError('Local API not connected. Start Docker Compose or select Synthetic preview.')}
    }
    refresh()
    const id=setInterval(refresh,5000)
    return()=>{cancelled=true;clearInterval(id)}
  },[mode])
  const items=mode==='demo'?fixtures:live.items
  const summary=mode==='demo'?summarize(fixtures):live.summary
  const chart=mode==='demo'?trending(fixtures):live.trends
  const series=chart.map(r=>({...r,time:new Date(r.minute).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}))
  const queue=useMemo(()=>items.filter(r=>r.anomaly&&
    (filter==='all'||(filter==='open'&&['new','investigating'].includes(r.status))||r.status===filter)&&
    (service==='all'||r.service===service)&&
    (r.event_id+' '+r.reason+' '+r.service).toLowerCase().includes(term.toLowerCase())).slice(0,100),
  [items,filter,service,term])
  async function triage(row,next) {
    setBusy(row.event_id)
    try {
      if(mode==='demo')setFixtures(old=>old.map(r=>r.event_id===row.event_id?{...r,status:next}:r))
      else {
        const headers={'Content-Type':'application/json'}
        if(token)headers.Authorization='Bearer '+token
        const response=await fetch('/api/events/'+encodeURIComponent(row.event_id)+'/status',{method:'PATCH',headers,body:JSON.stringify({status:next})})
        if(!response.ok)throw Error(response.status===401?'Bearer token required for triage':'Triage update failed')
        const replacement=await response.json()
        setLive(old=>({...old,items:old.items.map(r=>r.event_id===row.event_id?replacement:r)}))
      }
    } catch(e){setError(e.message)}finally{setBusy('')}
  }
  const tiles=[
    {label:'Processed events',value:count(summary?.events,0),note:'Persisted in the past hour',icon:Database},
    {label:'Detected anomalies',value:count(summary?.anomalies,0),note:count((summary?.anomaly_rate||0)*100)+'% of events',icon:AlertTriangle},
    {label:'End-to-end p95',value:summary?.p95_e2e_ms==null?'—':count(summary.p95_e2e_ms)+' ms',note:'Event to database record',icon:Timer},
    {label:'Open investigations',value:count(summary?.pending,0),note:'New and investigating',icon:Bell}
  ]
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="mark"><Activity size={22}/></div><div><strong>STREAMWATCH</strong><small>AI / OBSERVABILITY</small></div></div>
      <p className="navlabel">WORKSPACE</p>
      <a className="nav active" href="#overview"><Layers3 size={17}/> Overview</a>
      <a className="nav" href="#investigations"><ShieldCheck size={17}/> Investigations <b>{summary?.pending||0}</b></a>
      <p className="navlabel secondary">ENGINEERING</p>
      <a className="nav" href="https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection/tree/main/docs" target="_blank" rel="noreferrer"><Workflow size={17}/> Architecture <ArrowUpRight size={13}/></a>
      <a className="nav" href="https://github.com/harshakavali81-collab/Real-Time-Streaming-Anomaly-Detection" target="_blank" rel="noreferrer"><Database size={17}/> Source code <ArrowUpRight size={13}/></a>
      <div className="sidebar-foot"><div className="indicator">● {mode==='demo'?'SYNTHETIC PREVIEW':error?'API DISCONNECTED':'API CONNECTED'}</div><p>Local-first educational prototype. Never assume production monitoring.</p></div>
    </aside>
    <main className="content" id="overview">
      <header className="header"><div><span className="eyebrow">OPERATIONS / REAL-TIME INTELLIGENCE</span><h1>Streaming Intelligence</h1><p>Detect abnormal service telemetry. Investigate suspicious event patterns.</p></div><div className="actions"><label>Data source <select aria-label="Select data source" value={mode} onChange={e=>{setMode(e.target.value);setError('')}}><option value="live">Connected API</option><option value="demo">Synthetic preview</option></select></label><button onClick={()=>saveCSV(queue)}><Download size={15}/> Export queue</button></div></header>
      {mode==='demo'?<div className="notice"><AlertTriangle size={17}/> SYNTHETIC PREVIEW · In-browser fixtures, not measurements of Kafka or any external system.</div>:error?<div className="notice error"><AlertTriangle size={17}/>{error}<button onClick={()=>setMode('demo')}>Open preview</button></div>:<div className="connected">● API connected · refreshes every 5 seconds · last response {last||'pending'}</div>}
      <div className="section-header"><div><span className="eyebrow">01 / OPERATIONAL OVERVIEW</span><h2>System pulse <small>· rolling 60 minutes</small></h2></div><span className="pill">LOCAL / EDUCATIONAL</span></div>
      <section className="tiles">{tiles.map(({label,value,note,icon:Icon})=><article className="tile" key={label}><div className="tile-title"><span>{label}</span><Icon size={18}/></div><strong>{value}</strong><small>{note}</small></article>)}</section>
      <section className="charts">
        <article className="panel"><div className="panel-title"><div><span className="eyebrow">EVENT PROCESSING</span><h3>Throughput &amp; anomaly spikes</h3></div><span className="legend">● events &nbsp; <em>●</em> anomalies</span></div><div className="chart">
          {series.length?<ResponsiveContainer width="100%" height="100%"><AreaChart data={series}><defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#66eecb" stopOpacity=".24"/><stop offset="100%" stopColor="#66eecb" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#20394d" strokeDasharray="3 7" vertical={false}/><XAxis dataKey="time" tick={{fill:'#90acc1',fontSize:10}} minTickGap={35} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#90acc1',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#152c40',borderColor:'#34586c',borderRadius:10}}/><Area dataKey="events" type="monotone" stroke="#66eecb" strokeWidth={2} fill="url(#fill)"/><Area dataKey="anomalies" type="monotone" stroke="#f6b86d" strokeWidth={2} fill="transparent"/></AreaChart></ResponsiveContainer>:<div className="empty">Waiting for data from the producer and consumer.</div>}</div></article>
        <article className="panel"><div className="panel-title"><div><span className="eyebrow">DETECTION ENGINE</span><h3>Risk score trend</h3></div></div><div className="chart short">{series.length?<ResponsiveContainer width="100%" height="100%"><BarChart data={series}><CartesianGrid stroke="#20394d" strokeDasharray="3 7" vertical={false}/><XAxis dataKey="time" minTickGap={40} tick={{fill:'#90acc1',fontSize:10}} axisLine={false} tickLine={false}/><YAxis tick={{fill:'#90acc1',fontSize:10}} axisLine={false} tickLine={false}/><Tooltip contentStyle={{background:'#152c40',borderColor:'#34586c'}}/><Bar dataKey="avg_score" fill="#7ca6fa" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer>:<div className="empty">No model output yet.</div>}</div>
          <div className="diagnostics"><p>Simulator precision <b>{summary?.evaluation?.precision==null?'—':count(summary.evaluation.precision*100)+'%'}</b></p><p>Simulator recall <b>{summary?.evaluation?.recall==null?'—':count(summary.evaluation.recall*100)+'%'}</b></p><p>Events / minute <b>{count(summary?.rate_per_minute,2)}</b></p></div><small className="caveat">Precision and recall only use simulator labels; not real-world model validation.</small>
        </article>
      </section>
      <section className="panel queue" id="investigations"><div className="panel-title"><div><span className="eyebrow">02 / HUMAN-IN-THE-LOOP</span><h3>Investigation queue</h3></div><span className="pill">{queue.length} alerts</span></div>
        <div className="toolbar"><label className="search"><Search size={15}/><input aria-label="Search events" value={term} onChange={e=>setTerm(e.target.value)} placeholder="Find ID, service, reason..."/></label><select aria-label="Filter case status" value={filter} onChange={e=>setFilter(e.target.value)}>{['open','all','new','investigating','resolved','dismissed'].map(x=><option key={x} value={x}>{x}</option>)}</select><select aria-label="Filter service" value={service} onChange={e=>setService(e.target.value)}>{['all','checkout','payments','search','identity'].map(x=><option key={x} value={x}>{x}</option>)}</select></div>
        <div className="table-scroll"><table><thead><tr><th>EVENT / SERVICE</th><th>RISK SCORE</th><th>DETECTION SIGNAL</th><th>SEVERITY</th><th>STATUS</th><th>REVIEW</th></tr></thead><tbody>{queue.length?queue.map(row=><tr key={row.event_id}><td><strong>{row.service}</strong><small>{row.event_id.slice(0,18)} · {new Date(row.timestamp).toLocaleTimeString()}</small></td><td className="risk">{count(row.score,2)}</td><td>{row.reason}</td><td><span className={'severity '+row.severity}>{row.severity}</span></td><td>{row.status}</td><td><select disabled={busy===row.event_id} aria-label={'Update '+row.event_id} value={row.status} onChange={e=>triage(row,e.target.value)}>{['new','investigating','resolved','dismissed'].map(x=><option key={x}>{x}</option>)}</select></td></tr>):<tr><td colSpan="6" className="empty">No matching alerts.</td></tr>}</tbody></table></div>
        {mode==='live'&&<details className="auth"><summary>Optional API bearer token for protected triage</summary><input type="password" aria-label="API bearer token" placeholder="Paste bearer token (not persisted)" value={token} onChange={e=>setToken(e.target.value)}/></details>}
      </section>
      <footer><span>StreamWatch AI · Redpanda / Kafka · Python · SQL · React</span><span>Simulated telemetry only · Not an operational security service</span></footer>
    </main>
  </div>
}
createRoot(document.getElementById('root')).render(<App/>)
