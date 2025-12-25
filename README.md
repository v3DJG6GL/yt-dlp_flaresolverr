_NOTE: This setup was made with the help of AI_

# yt-dlp FlareSolverr Proxy

This setup integrates **FlareSolverr** with **yt-dlp** using **mitmproxy**. It uses a proxy server that handles Cloudflare challenges by intercepting requests and solving them on the fly.

## Files
*   `docker-compose.yml`: Orchestrates the `flaresolverr` and `mitmproxy` services using host networking.
*   `yt-dlp_flaresolverr.py`: A `mitmproxy` addon script. It detects blocked responses, queries FlareSolverr for a solution, and updates the request headers (Cookies/User-Agent) automatically.

## Usage

### 1. Download the Repository
Clone the repository to your local machine and navigate into the directory:

    git clone https://github.com/v3DJG6GL/yt-dlp_flaresolverr.git &&
    cd yt-dlp_flaresolverr

### 2. Start the Proxy Stack
Start the services using Docker Compose:

    docker-compose up -d

### 3. Monitor Status & Logs
If you encounter issues or want to watch the solving process (to see when `mitmproxy` detects a block and `flaresolverr` solves it), you can view the container logs:

    # (Optional) Verify the project is running
    docker compose ls

    # Stream logs to see the "Block detected" and "Solved!" messages
    docker compose logs -f

### 4. Run yt-dlp
Direct `yt-dlp` to use the local proxy running on port 8192.

    yt-dlp --proxy http://127.0.0.1:8192 --no-check-certificate <VIDEO_URL>

### 5. Verification
If a site is protected by Cloudflare:
1.  `yt-dlp` makes a request.
2.  `mitmproxy` receives a 403/503.
3.  The python script logs: `🛑 Block detected... 🚀 Asking FlareSolverr to solve...`.
4.  Once solved (`✅ Solved!`), `yt-dlp` receives the correct content and begins downloading.

## Configuration Details
*   **Network**: The setup uses `network_mode: host` to simplify communication between containers and localhost.
*   **Dependencies**: The `mitmproxy` container installs `requests` at runtime to communicate with the FlareSolverr API.
