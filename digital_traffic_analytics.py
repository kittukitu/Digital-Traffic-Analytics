import argparse
import google.generativeai as genai

# 🔑 Configure Gemini
genai.configure(api_key="AIzaSyC2EVCSgC-DRWVunkKi7Ro0J1upoN3UglE")
model = genai.GenerativeModel("gemini-1.5-flash")

def predict_traffic(current_visitors, bounce_rate, avg_session_duration, marketing_score):
    try:
        # Simple predictive formula (can replace with ML model later)
        predicted_visitors = current_visitors * (1 + marketing_score*0.3 - bounce_rate*0.5)
        engagement_score = avg_session_duration / 300  # normalize assuming 5 min avg session
        traffic_quality = "High" if engagement_score > 0.6 else "Medium" if engagement_score > 0.3 else "Low"

        prompt = f"""
        You are a Digital Traffic Analytics AI.
        Given the following inputs:

        - Current Visitors: {current_visitors}
        - Bounce Rate: {bounce_rate}
        - Avg. Session Duration (seconds): {avg_session_duration}
        - Marketing Score (0-1): {marketing_score}
        - Predicted Visitors: {predicted_visitors:.2f}
        - Engagement Score: {engagement_score:.2f} ({traffic_quality})

        Provide:
        1. A strategy to improve website traffic and user engagement.
        2. A professional explanation why this strategy works.
        """

        response = model.generate_content(prompt)
        ai_text = response.text if response else "❌ No response from AI"

        parts = ai_text.split("\n", 1)
        strategy = parts[0].strip() if parts else "Not generated"
        explanation = parts[1].strip() if len(parts) > 1 else ai_text

        print("\n📊 Traffic Prediction Results")
        print(f"Predicted Visitors: {predicted_visitors:.2f}")
        print(f"Engagement Score: {engagement_score:.2f}")
        print(f"Traffic Quality: {traffic_quality}")
        print(f"Suggested Strategy: {strategy}")
        print("\nAI Explanation:")
        print(explanation)

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digital Traffic Analytics AI (Terminal Version)")
    parser.add_argument("--current_visitors", type=float, help="Current number of website visitors")
    parser.add_argument("--bounce_rate", type=float, help="Bounce rate (0-1)")
    parser.add_argument("--avg_session_duration", type=float, help="Average session duration in seconds")
    parser.add_argument("--marketing_score", type=float, help="Marketing effectiveness score (0-1)")

    args = parser.parse_args()

    current_visitors = args.current_visitors if args.current_visitors is not None else float(input("Enter Current Visitors: "))
    bounce_rate = args.bounce_rate if args.bounce_rate is not None else float(input("Enter Bounce Rate (0-1): "))
    avg_session_duration = args.avg_session_duration if args.avg_session_duration is not None else float(input("Enter Avg. Session Duration (seconds): "))
    marketing_score = args.marketing_score if args.marketing_score is not None else float(input("Enter Marketing Score (0-1): "))

    predict_traffic(current_visitors, bounce_rate, avg_session_duration, marketing_score)
