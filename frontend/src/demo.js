// Fixtures for a labelled synthetic browser preview only; NOT Kafka or API observations.
export function demoFixtures() {
  const services = ['checkout','payments','search','identity']
  const base = Date.now()
  return Array.from({length:190},(_,i)=>{
    const anomaly = i%13===0||i%29===0
    const score = anomaly ? +(4.4+(i%5)*.45).toFixed(2): +(0.8+(i%10)*.23).toFixed(2)
    return {event_id:'synthetic-'+i,service:services[i%4],timestamp:new Date(base-(190-i)*12000).toISOString(),
      anomaly,score,severity:anomaly?(score>=5.5?'critical':'high'):'normal',
      reason:anomaly?'latency deviation':'within baseline',status:'new',model:'online-zscore-v1',
      source:'simulator',ground_truth:anomaly,processing_ms:1.5,e2e_latency_ms:25+i%9*2.6,
      features:{latency_ms:anomaly?1050+i%7*60:95+i%19*9,cpu_pct:anomaly?92:25+i%35,
                error_rate:anomaly?.29:.008,rps:85+i%45}}
  }).reverse()
}
export function summarize(items) {
  const anomalies=items.filter(x=>x.anomaly)
  const pending=anomalies.filter(x=>['new','investigating'].includes(x.status)).length
  const tp=anomalies.filter(x=>x.ground_truth===true).length
  const fp=anomalies.filter(x=>x.ground_truth===false).length
  const fn=items.filter(x=>!x.anomaly&&x.ground_truth===true).length
  return {events:items.length,anomalies:anomalies.length,pending,rate_per_minute:+(items.length/60).toFixed(2),
    anomaly_rate:anomalies.length/Math.max(items.length,1),p95_e2e_ms:47.4,p95_processing_ms:2.4,
    evaluation:{labelled:items.length,dataset:'simulator labels only',
      precision:tp+fp?tp/(tp+fp):null,recall:tp+fn?tp/(tp+fn):null,tp,fp,fn}}
}
export function trending(items) {
  const buckets={}
  items.forEach(e=>{
    const k=e.timestamp.slice(0,16)
    if(!buckets[k])buckets[k]={minute:k,events:0,anomalies:0,scores:0,latencies:0}
    const b=buckets[k]
    b.events++;b.anomalies+=Number(e.anomaly);b.scores+=e.score;b.latencies+=e.e2e_latency_ms
  })
  return Object.values(buckets).sort((a,b)=>a.minute.localeCompare(b.minute)).map(b=>({
    minute:b.minute,events:b.events,anomalies:b.anomalies,
    avg_score:+(b.scores/b.events).toFixed(2),avg_latency_ms:+(b.latencies/b.events).toFixed(2)}))
}
