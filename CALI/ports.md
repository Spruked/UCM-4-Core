# OFFICIAL PORT ASSIGNMENTS

## ✅ OFFICIAL PORT ASSIGNMENTS (CANONICAL)

### **UCM / CALI**

* **8080** — Cognitive Engine (UCM Core)
* **5050** — CALI State / Control API
* **8765** — CALI WebSocket / Orb Bridge

### **DALS**

* **8003** — DALS Core API (ISS / routing / observability)
* **8008** — DALS Dashboard UI
* **8000** — ❌ *Retired / Do Not Use*

### **GOAT**

* **5173** — GOAT Frontend (primary)
* **5000** — GOAT Backend / API

### **TrueMark**

* **8081** — TrueMark Core API

### **CertSig**

* **8082** — CertSig Signature Engine

### **Reserved / Optional**

* **6379** — Redis (optional; never required for DALS startup)
* **3000** — Dev-only frontend testing (optional)

---

**Directive:**
All services **must bind only to the ports above**. Any deviation is a configuration error.</content>
<parameter name="filePath">c:\dev\Desktop\UCM_4_Core\ports.md