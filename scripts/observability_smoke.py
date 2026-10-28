"""Black-box validation for the OPTIONAL local Prometheus + Grafana overlay."""
import json
import time
from urllib.request import urlopen

def get_json(url):
    with urlopen(url,timeout=8) as result:
        return json.load(result)

def until(call, label, timeout=100):
    end=time.monotonic()+timeout
    error=None
    while time.monotonic()<end:
        try:
            result=call()
            if result:
                return result
        except Exception as exc:
            error=exc
        time.sleep(2)
    raise AssertionError(f"{label} not ready; last error={error}")

def main():
    prom=until(lambda: get_json("http://localhost:9090/api/v1/rules"),
               "Prometheus rule API")
    groups=prom.get("data",{}).get("groups",[])
    assert prom.get("status")=="success"
    assert any(group.get("name")=="streamwatch-local-alerts" for group in groups), (
        "Expected streamwatch-local-alerts Prometheus rule group")
    health=until(lambda: get_json("http://localhost:3000/api/health"),"Grafana health")
    assert health.get("database")=="ok"
    dashboards=until(lambda: [x for x in get_json(
        "http://localhost:3000/api/search?query=StreamWatch")
        if "StreamWatch" in x.get("title","")], "provisioned Grafana dashboard")
    assert dashboards
    print(json.dumps({"result":"PASS",
                      "prometheus_rules_loaded":True,
                      "grafana_database":health["database"],
                      "provisioned_dashboard_title":dashboards[0]["title"],
                      "scope":"local ephemeral synthetic monitoring"},indent=2))

if __name__=="__main__":
    main()
