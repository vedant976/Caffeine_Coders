import time
import threading
import random
from datetime import datetime
from backend.app.core.metrics import global_metrics
from backend.app.core.routing import global_routing
from backend.simulator.engine import sim_state

class PaymentAgent:
    def __init__(self):
        self.logs = []
        self.active = True
        
        # Simulated "Knowledge Base" for General Queries
        self.knowledge_base = {
            "what is sentinelpay": "SentinelPay is an autonomous payment operations agent designed to monitor, route, and self-heal payment transaction streams in real-time.",
            "what is success rate": "Success Rate (SR) is the percentage of transactions that complete successfully. We target >99% globally.",
            "what is latency": "Latency is the time taken for a transaction to process. High latency (>400ms) can lead to user drop-offs.",
            "how do you work": "I operate on a continuous O-R-D-A-L loop: Observe data, Reason about patterns, Decide on actions, Act on infrastructure, and Learn from results.",
            "who built you": "I was engineered by the Advanced Agentic Coding Team at Google Deepmind.",
            "help": "I can help you monitor bank status (e.g., 'Status of SBI'), fix issues (e.g., 'Scale HDFC'), or answer questions about the system."
        }
        
    def log(self, stage: str, message: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stage": stage,
            "message": message
        }
        self.logs.insert(0, entry) # Newest first
        self.logs = self.logs[:50] # Keep last 50
    
    def reason_and_act(self):
        stats = global_metrics.get_stats()
        by_issuer = stats.get("by_issuer", {})
        
        self.log("Observe", f"Analyzed {stats['total']} transactions. Global SR: {stats['success_rate']:.2f}")
        
        found_issue = False
        for issuer, data in by_issuer.items():
            sr = data["success_rate"]
            
            # Autonomous Healing Trigger
            if sr < 0.95 and data["volume"] > 0:
                found_issue = True
                self.log("Reason", f"Detected drop in {issuer} (SR: {sr:.2f}). Initiating Autonomous Recovery.")
                
                # Action 1: attempt scaling first
                if sim_state.get_issuer_health(issuer) < 1.0:
                    self.log("Decide", f"Attempting to scale cloud infrastructure for {issuer} to improve SR.")
                    sim_state.scale_infrastructure(issuer)
                    self.log("Act", f"Scaled Up {issuer} resources. Monitoring for improvement.")
                
                # Action 2: Disable route
                elif global_routing.is_enabled(issuer):
                    self.log("Decide", f"Scaling ineffective. Disabling route to {issuer} to protect Global SR.")
                    global_routing.set_route(issuer, False)
                    self.log("Act", f"Action Executed: Route {issuer} -> DISABLED.")
                else:
                    self.log("Decide", f"Route {issuer} is already disabled.")
            
            # Re-enable if healthy (Simulated recovery)
            elif sr > 0.99 and not global_routing.is_enabled(issuer):
                 # In a real system, we would probe. Here, we can occasionally re-enable.
                 pass

        if not found_issue:
            self.log("Reason", "System operating within normal parameters.")

    def start_loop(self):
        def loop():
            while self.active:
                self.reason_and_act()
                time.sleep(5)
        
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def chat(self, message: str) -> str:
        msg = message.lower().strip()
        stats = global_metrics.get_stats()
        
        # --- NLU LAYER ---
        
        # 1. Action Intents (Highest Priority)
        if any(w in msg for w in ["scale", "boost", "fix", "repair", "heal"]):
            return self._handle_action(msg, stats)

        # 2. Specific Entity Queries
        # Check if user mentioned any bank name
        mentioned_issuers = [i for i in stats.get("by_issuer", {}) 
                           if i in msg or i.replace("_", " ") in msg or i.split("_")[0] in msg]
        if mentioned_issuers:
            # If specifically asking about "status", "latency", "health" of that bank
            return self._handle_entity_query(mentioned_issuers[0], stats)

        # 3. Global Dashboard / Overview
        if any(w in msg for w in ["status", "report", "overview", "dashboard", "health", "metrics"]):
            return self._handle_global_status(stats)
            
        # 4. Alerts / Incidents
        if any(w in msg for w in ["alert", "error", "fail", "issue", "bug", "problem"]):
            return self._handle_alerts(stats)
            
        # 5. Knowledge Base (Q&A)
        for key, answer in self.knowledge_base.items():
            if key in msg:
                return f"💡 **{answer}**"
                
        # 6. Small Talk / Identity
        if any(w in msg for w in ["hello", "hi", "hey", "greetings"]):
            responses = [
                "👋 Hello! I am SentinelPay, ready to monitor your transactions.",
                "High performance detected. How can I assist you in Operations today?",
                "Greetings. All systems are green. What's on your mind?"
            ]
            return random.choice(responses)

        # 7. Fallback (Universal "LLM-like" response)
        return (f"🤔 I'm analyzing your request: *'{message}'*...\n\n"
                "As an operational agent, my expertise is in **Transaction Monitoring**, **Cloud Scaling**, and **Route Optimization**.\n"
                "Try asking:\n"
                "- *'What is the latency of SBI?'*\n"
                "- *'Scale HDFC infrastructure'*\n"
                "- *'Show me global health'*")

    # --- HANDLERS ---

    def _handle_action(self, msg, stats):
        for issuer in stats.get("by_issuer", {}):
            simple = issuer.split("_")[0]
            if issuer in msg or issuer.replace("_", " ") in msg or simple in msg:
                success = sim_state.scale_infrastructure(issuer)
                if success:
                    self.log("Act", f"Chat Command: Scaled {issuer}.")
                    return f"🚀 **Action Confirmed:** I have provisioned additional compute units for **{issuer.replace('_', ' ').title()}**. You should see latency drop within seconds."
                return f"⚠️ **{issuer.replace('_', ' ').title()}** is already running at **100% capacity**. Further scaling is not possible."
        return "I can scale infrastructure, but I need to know which bank. Try saying **'Scale ICICI'**."

    def _handle_entity_query(self, issuer, stats):
        data = stats["by_issuer"][issuer]
        active = global_routing.is_enabled(issuer)
        clean_name = issuer.replace("_", " ").title()
        
        # Dynamic commentary based on metrics
        comment ="Performance is optimal."
        if data['success_rate'] < 0.95: comment = "Performance is degraded. recommending inspection."
        if data['avg_latency'] > 300: comment += " Latency is higher than average."
        
        status_icon = "🟢" if data['success_rate'] >= 0.95 else "🔴"
        
        return (f"{status_icon} **{clean_name} Analysis**\n"
                f"• **Status**: {'✅ Active' if active else '⛔ Rerouted'}\n"
                f"• **Success Rate**: {data['success_rate']*100:.1f}%\n"
                f"• **Latency**: {data['avg_latency']:.0f}ms\n"
                f"• **Insight**: {comment}")

    def _handle_global_status(self, stats):
        sr = stats['success_rate'] * 100
        total = stats['total']
        
        if sr > 98:
            return f"🌍 **Global Systems Nominal**\nCurrently processing **{total} TPM** with a **{sr:.1f}%** success rate. All payment rails are fully operational."
        elif sr > 90:
             return f"⚠️ **Minor Turbulence**\nGlobal Success Rate is **{sr:.1f}%**. I am actively optimizing routes to mitigate impact."
        else:
             return f"🚨 **Critical System Alert**\nSuccess Rate has dropped to **{sr:.1f}%**. Immediate attention required on failing banks."

    def _handle_alerts(self, stats):
        issues = []
        for issuer, data in stats.get("by_issuer", {}).items():
            if data['success_rate'] < 0.95:
                issues.append(f"**{issuer.replace('_',' ').title()}** (SR: {data['success_rate']*100:.1f}%)")
        
        if issues:
            return f"👮 **Active Incidents Report**\nThinking... I have detected anomalies in: {', '.join(issues)}. autonomous recovery is active."
        return "🛡️ **Security Scan Complete**\nNo active alerts. The system is stable."

global_agent = PaymentAgent()
