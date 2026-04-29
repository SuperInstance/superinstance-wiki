import json, sys

# Read the HTML file
with open('/root/.openclaw/workspace/cocapn-live-v2.html', 'r') as f:
    html = f.read()

# Split into chunks of ~8KB to avoid command length limits
chunk_size = 8000
chunks = [html[i:i+chunk_size] for i in range(0, len(html), chunk_size)]

print(f"File size: {len(html)} bytes")
print(f"Chunks: {len(chunks)}")

# Generate curl commands for each chunk
for i, chunk in enumerate(chunks):
    # Escape for JSON
    escaped = chunk.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    if i == 0:
        cmd = f'python3 -c "html = \\\'{escaped}\\\'; open(\\\'/home/ubuntu/.openclaw/workspace/data/cocapn-live-v2.html\\\', \\\'w\\\').write(html)"'
    else:
        cmd = f'python3 -c "html = \\\'{escaped}\\\'; open(\\\'/home/ubuntu/.openclaw/workspace/data/cocapn-live-v2.html\\\', \\\'a\\\').write(html)"'
    print(f"\n--- Chunk {i+1}/{len(chunks)} ---")
    print(f"curl -s -X POST http://147.224.38.131:8848/cmd -H 'Content-Type: application/json' -d '{{\"agent\":\"ccc\",\"tool\":\"shell\",\"command\":\"{cmd}\"}}'")
