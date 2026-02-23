import httpx, os, sys, time

base = "http://127.0.0.1:8003"
s = httpx.Client(base_url=base, follow_redirects=True)
print("Index", s.get("/").status_code)
r = s.get("/signup")
print("GET /signup", r.status_code)
r = s.post("/signup", data={"name":"Tester","email":"tester@example.com","password":"secret"})
print("Signup", r.status_code)
print("Dashboard", s.get("/dashboard").status_code)
with open(os.path.join(os.getcwd(),"sample.txt"), "rb") as f:
    r = s.post("/analyze", files={"file":("document.txt", f, "text/plain")}, data={"features":"full"})
print("Analyze submit", r.status_code)
time.sleep(1)
h = s.get("/history")
print("History", h.status_code, "items listed:", "Analysis History" in h.text)
