There is an access log in the working directory (`/app/access.log`). Analyze the traffic and summarize what you find by writing a JSON report to `/app/report.json`.

The success criteria are:
1. Parse `/app/access.log`.
2. Compute `total_requests` (the total number of request entries in the log file).
3. Compute `unique_ips` (the number of unique client IP addresses).
4. Compute `top_path` (the most frequently requested path).
5. Save these findings to a JSON file at `/app/report.json` with the keys `total_requests`, `unique_ips`, and `top_path`.
