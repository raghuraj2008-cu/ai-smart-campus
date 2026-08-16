from typing import Dict, Any

class RiskPredictor:
    """
    Predictive intelligence for campus risk assessment, safety analysis, and maintenance priority modeling.
    """
    def predict_location_risk(self, location: str, issue_type: str) -> Dict[str, Any]:
        risk_score = 0.2  # Base risk level
        
        high_risk_locations = ["lab", "server room", "substation", "chemistry", "basement"]
        critical_issues = ["fire", "smoke", "short circuit", "chemical leak", "gas", "collapse"]

        if any(loc in location.lower() for loc in high_risk_locations):
            risk_score += 0.35

        if any(issue in issue_type.lower() for issue in critical_issues):
            risk_score += 0.45

        risk_score = min(risk_score, 1.0)

        risk_level = "LOW"
        if risk_score > 0.7:
            risk_level = "CRITICAL"
        elif risk_score > 0.4:
            risk_level = "HIGH"

        return {
            "location": location,
            "issue_type": issue_type,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "requires_immediate_dispatch": risk_score >= 0.75
        }

risk_predictor = RiskPredictor()