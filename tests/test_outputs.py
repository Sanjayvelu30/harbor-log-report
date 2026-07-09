import json
from pathlib import Path


def test_criterion_1_parse_access_log():
    """Verify Success Criterion 1: Parse /app/access.log."""
    # Ensure the input log exists in the workspace
    assert Path("/app/access.log").exists(), "/app/access.log does not exist"


def test_criterion_2_total_requests():
    """Verify Success Criterion 2: Compute total_requests (the total number of request entries in the log file)."""
    path = Path("/app/report.json")
    assert path.exists(), "report.json does not exist"
    with open(path) as f:
        data = json.load(f)
    assert data.get("total_requests") == 6, f"Expected 6 total requests, got {data.get('total_requests')}"


def test_criterion_3_unique_ips():
    """Verify Success Criterion 3: Compute unique_ips (the number of unique client IP addresses)."""
    path = Path("/app/report.json")
    assert path.exists(), "report.json does not exist"
    with open(path) as f:
        data = json.load(f)
    assert data.get("unique_ips") == 3, f"Expected 3 unique IPs, got {data.get('unique_ips')}"


def test_criterion_4_top_path():
    """Verify Success Criterion 4: Compute top_path (the most frequently requested path)."""
    path = Path("/app/report.json")
    assert path.exists(), "report.json does not exist"
    with open(path) as f:
        data = json.load(f)
    assert data.get("top_path") == "/index.html", f"Expected top path to be '/index.html', got {data.get('top_path')}"


def test_criterion_5_save_json_report():
    """Verify Success Criterion 5: Save findings to a JSON file at /app/report.json with keys total_requests, unique_ips, and top_path."""
    path = Path("/app/report.json")
    assert path.exists(), "report.json does not exist"
    with open(path) as f:
        data = json.load(f)
    assert "total_requests" in data, "total_requests key is missing"
    assert "unique_ips" in data, "unique_ips key is missing"
    assert "top_path" in data, "top_path key is missing"


