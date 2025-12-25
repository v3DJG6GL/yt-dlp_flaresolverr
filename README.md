_NOTE: This setup was made with the help of AI_

# yt-dlp FlareSolverr Proxy (Docker)

This setup integrates **FlareSolverr** with **yt-dlp** using **mitmproxy**. Instead of a direct plugin, it uses a proxy server that transparently handles Cloudflare challenges (403/503 errors) by intercepting requests and solving them on the fly.

## Files
*   `docker-compose.yml`: Orchestrates the `flaresolverr` and `mitmproxy` services using host networking.
*   `yt-dlp_flaresolverr.py`: A `mitmproxy` addon script. It detects blocked responses, queries FlareSolverr for a solution, and updates the request headers (Cookies/User-Agent) automatically.

## Usage

### 1. Start the Proxy Stack
Ensure both files are in the same directory, then start the services:

    docker-compose up -d

### 2. Monitor Status & Logs
It is highly recommended to open a separate terminal window to monitor the logs. This allows you to see when `mitmproxy` detects a block and when `flaresolverr` successfully solves it.

    # (Optional) Verify the project is running
    docker compose ls

    # Stream logs to see the "Block detected" and "Solved!" messages
    docker compose logs -f

### 3. Run yt-dlp
Direct `yt-dlp` to use the local proxy running on port 8192.

    yt-dlp --proxy http://127.0.0.1:8192 --no-check-certificate <VIDEO_URL>

### 3. Verification
If a site is protected by Cloudflare:
1.  `yt-dlp` makes a request.
2.  `mitmproxy` receives a 403/503.
3.  The python script logs: `🛑 Block detected... 🚀 Asking FlareSolverr to solve...`.
4.  Once solved (`✅ Solved!`), `yt-dlp` receives the correct content and begins downloading.

## Configuration Details
*   **Network**: The setup uses `network_mode: host` (Linux only) to simplify communication between containers and localhost.
*   **Dependencies**: The `mitmproxy` container installs `requests` at runtime to communicate with the FlareSolverr API.
