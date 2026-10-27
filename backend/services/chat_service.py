"""
Rule-Based Virtual Assistant Service for InsureVisionAI.
Provides safety steps, insurance filing advice, emergency dispatch guidance,
hospitals, towing, and accident report assistance without requiring external paid LLM APIs.
"""

from typing import Any, Dict, List


SAFETY_DISCLAIMER = (
    "This virtual assistant provides automated simulation guidance and does not "
    "replace emergency services (dial 112 or 108 in India) or formal legal and insurance counsel."
)


class ChatService:
    @staticmethod
    def answer(user_message: str) -> Dict[str, Any]:
        """
        Evaluate user message using keyword and intent matching.
        Returns safety-first structured advice and suggested quick actions.
        """
        msg = user_message.lower().strip()

        # 1. Accident Safety Steps
        if any(w in msg for w in ["what should i do", "accident", "crashed", "hit", "collision", "just happened", "safety"]):
            reply = (
                "Here are immediate safety steps to follow after an accident:\n"
                "1. Check for Injuries: Ensure yourself and passengers are safe. If anyone is injured, call 108/112 immediately.\n"
                "2. Move to Safety: If vehicles are drivable and obstructing traffic, move to the side of the road and turn on hazard flashers.\n"
                "3. Secure the Scene: Turn off engines, place warning triangles, and stay away from moving traffic.\n"
                "4. Document Telemetry & Evidence: Use InsureVisionAI to record the incident, photograph damage, and note the other vehicle's registration.\n"
                "5. Contact Support: Use the SOS or Assistance feature in the app to request nearby towing or medical services."
            )
            actions = ["Trigger SOS", "Find Nearby Services", "Simulate Incident"]

        # 2. Police & Emergency Services
        elif any(w in msg for w in ["police", "112", "emergency", "cop", "fir", "law", "station"]):
            reply = (
                "Emergency & Police Guidelines:\n"
                "- Unified Emergency Helpline in India: Call 112\n"
                "- Police Helpline: Call 100 / 112\n"
                "- For motor vehicle accidents involving third-party property damage or bodily injury, filing a First Information Report (FIR) or police intimation is mandatory for legal and insurance claims.\n"
                "- Do not engage in roadside altercations; remain calm and let traffic authorities assess the scene."
            )
            actions = ["Call Emergency (112)", "Emergency Contacts", "Accident Report"]

        # 3. Hospitals & Medical Services
        elif any(w in msg for w in ["hospital", "ambulance", "doctor", "injury", "injured", "bleed", "medical", "108"]):
            reply = (
                "Medical Emergency Assistance:\n"
                "- Emergency Ambulance Helpline: Call 108 or 102 immediately.\n"
                "- If anyone is unconscious, experiencing chest pain, or has suspected neck/spine trauma, DO NOT move them unless there is an immediate fire hazard.\n"
                "- Check the 'Nearby Services' section in InsureVisionAI for verified hospitals, trauma centers, and estimated travel times."
            )
            actions = ["Nearby Hospitals", "Trigger SOS", "Emergency Contacts"]

        # 4. Towing & Roadside Mechanics
        elif any(w in msg for w in ["tow", "towing", "mechanic", "breakdown", "flat tire", "engine", "stuck", "repair"]):
            reply = (
                "Roadside Assistance & Towing:\n"
                "- If your vehicle is immobilized, request towing via the 'Physical Assistance' module.\n"
                "- Check the 'Nearby Services' screen for 24/7 towing providers and authorized mechanics in your vicinity.\n"
                "- Ensure your vehicle is locked and valuables are removed before dispatching the tow truck."
            )
            actions = ["Request Towing", "Find Mechanics", "Assistance Status"]

        # 5. Insurance & Claims Guidance
        elif any(w in msg for w in ["insurance", "claim", "policy", "cashless", "surveyor", "deductible", "coverage"]):
            reply = (
                "Insurance Claim Filing Process:\n"
                "1. Intimate Your Insurer: Inform your provider (e.g. ICICI Lombard, HDFC ERGO, Bajaj Allianz, Tata AIG) within 24–48 hours.\n"
                "2. Keep Documents Ready: Policy schedule, driver's license, vehicle RC, and incident report.\n"
                "3. Digital Evidence: Download the InsureVisionAI Incident Report featuring sensor telemetry and fault analysis to substantiate your claim.\n"
                "4. Cashless Network Garages: Opt for insurer-network garages for cashless settlement after surveyor inspection."
            )
            actions = ["View Insurance", "Download Report", "Incident Analysis"]

        # 6. Fault Analysis & Liability
        elif any(w in msg for w in ["fault", "blame", "liability", "percentage", "who is at fault", "responsible", "red light"]):
            reply = (
                "Fault Attribution Telemetry Analysis:\n"
                "- InsureVisionAI evaluates speed compliance, traffic light signal state, braking responsiveness, and impact points.\n"
                "- For example, if the other vehicle violated a red light and was 15 km/h over the speed limit, they carry primary liability (e.g., 65%).\n"
                "- Note: InsureVisionAI analysis is for demonstrative estimation and does not represent a final court ruling."
            )
            actions = ["View Fault Analysis", "Simulate Incident", "Download Report"]

        # 7. Accident Reports & Downloads
        elif any(w in msg for w in ["report", "download", "pdf", "export", "summary", "document"]):
            reply = (
                "Accident Telemetry Reports:\n"
                "- You can view and download a comprehensive incident report in PDF or JSON format.\n"
                "- The report aggregates vehicle sensor data, speed analysis, braking telemetry, fault breakdown, and policy information.\n"
                "- Navigate to the Reports module or click below to export your latest report."
            )
            actions = ["Download PDF Report", "View Latest Incident", "Dashboard"]

        # Default Helpful Greeting
        else:
            reply = (
                "Hello! I am your InsureVisionAI Road Safety & Claims Assistant. I can assist you with:\n"
                "• Immediate post-accident safety steps and emergency protocols\n"
                "• Contacting emergency services (112 / 108) and local hospitals\n"
                "• Requesting 24/7 towing and roadside mechanics\n"
                "• Understanding fault telemetry analysis and liability factors\n"
                "• Filing insurance claims and downloading accident reports\n\n"
                "How can I assist you right now?"
            )
            actions = ["Accident Safety Steps", "Nearby Services", "Insurance Help", "Simulate Incident"]

        return {
            "reply": reply,
            "mode": "rule_based",
            "suggested_actions": actions,
            "disclaimer": SAFETY_DISCLAIMER
        }


chat_service = ChatService()
