from scripts.kafka_load import percentile, measure
import pytest

def test_percentiles():
    assert percentile([], .5) is None
    assert percentile([1,2,3,4,5], .95) == 4
    assert percentile([100], .95) == 100

@pytest.mark.parametrize("settings",[
    {"events": 0}, {"events": 1000001},
    {"rate": 0}, {"rate": -2}, {"rate": 20000},
    {"anomaly_rate": 1.1}
])
def test_rate_and_count_guards(settings):
    with pytest.raises(ValueError):
        measure(**settings)
