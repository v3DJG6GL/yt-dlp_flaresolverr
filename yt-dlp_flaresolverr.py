import json
import requests
from mitmproxy import http, ctx

# --- CONFIGURATION ---
FLARESOLVERR_URL = "http://127.0.0.1:8191/v1"
# ---------------------

class CloudflareSolver:
    def response(self, flow: http.HTTPFlow):
        # Trigger on 403 Forbidden or 503 Service Unavailable
        if flow.response.status_code in [403, 503]:
            # Detect Cloudflare or WAF block
            body = flow.response.text.lower()
            is_blocked = "cloudflare" in body or "just a moment" in body or "challenge" in body or "forbidden" in body
            
            if is_blocked:
                ctx.log.info(f"🛑 Block detected on {flow.request.url} (Status: {flow.response.status_code})")
                self.solve_challenge(flow)

    def solve_challenge(self, flow: http.HTTPFlow):
        original_url = flow.request.url
        ctx.log.info(f"🚀 Asking FlareSolverr to solve: {original_url}")
        
        payload = {
            "cmd": "request.get",
            "url": original_url,
            "maxTimeout": 60000,
        }

        try:
            res = requests.post(FLARESOLVERR_URL, json=payload, timeout=70)
            data = res.json()

            if data.get("status") == "ok":
                solution = data["solution"]
                final_url = solution["url"]
                
                ctx.log.info(f"✅ Solved! Original: {original_url} -> Final: {final_url}")

                # COOKIE HANDLING
                cookies = solution.get("cookies", [])
                cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                
                flow.request.headers["Cookie"] = cookie_header
                flow.request.headers["User-Agent"] = solution["userAgent"]

                # REDIRECT:
                # If FlareSolverr followed a redirect (URL changed), we must tell yt-dlp to redirect too.
                # yt-dlp needs the INTERMEDIATE redirect url with 'requestId'.
                if final_url != original_url:
                    ctx.log.info(f"🔄 Emulating Redirect to: {final_url}")
                    flow.response.status_code = 302
                    flow.response.headers["Location"] = final_url
                    flow.response.text = "" # Empty body for redirect
                    
                    # Inject cookies so the next request succeeds
                    for c in cookies:
                         flow.response.headers.add("Set-Cookie", f"{c['name']}={c['value']}; Path=/; Domain={c['domain']}")
                    return

                # If no redirect (or same URL), just return the content
                flow.response.status_code = solution["status"]
                flow.response.text = solution["response"]
                for c in cookies:
                     flow.response.headers.add("Set-Cookie", f"{c['name']}={c['value']}; Path=/; Domain={c['domain']}")
                
            else:
                ctx.log.error(f"❌ FlareSolverr failed: {data}")

        except Exception as e:
            ctx.log.error(f"💥 Connection to FlareSolverr failed: {e}")

addons = [
    CloudflareSolver()
]
