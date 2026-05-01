from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MEDICAL_INFO = {
    "departments": [
        "Cardiology",
        "Neurology",
        "Orthopedics",
        "Pediatrics",
        "Dermatology",
        "General Medicine",
    ],
    "appointment_hours": "Monday to Saturday, 9:00 AM to 6:00 PM",
    "appointment_methods": [
        "Call our reception at +92-300-1234567",
        "Visit front desk at Main Building",
        "Book online through the hospital portal",
    ],
    "doctors": [
        {
            "name": "Dr. Ayesha Khan",
            "specialty": "Cardiology",
            "days": "Mon, Wed, Fri",
        },
        {
            "name": "Dr. Bilal Ahmed",
            "specialty": "Neurology",
            "days": "Tue, Thu, Sat",
        },
        {
            "name": "Dr. Sana Iqbal",
            "specialty": "Pediatrics",
            "days": "Mon to Thu",
        },
        {
            "name": "Dr. Umar Farooq",
            "specialty": "Orthopedics",
            "days": "Mon, Tue, Fri",
        },
        {
            "name": "Dr. Hina Saleem",
            "specialty": "Dermatology",
            "days": "Wed, Thu, Sat",
        },
    ],
    "location": "Medical Center, Block A, Lahore",
    "emergency": "For emergency, call 1122 or our emergency desk: +92-42-111-999-000",
}

def format_doctor_list():
    lines = []
    for doctor in MEDICAL_INFO["doctors"]:
        line = f"{doctor['name']} - {doctor['specialty']} ({doctor['days']})"
        lines.append(line)
    return "\n".join(lines)

def get_bot_reply(user_message):
    msg = user_message.lower().strip()
    
    if not msg:
        return "Please type your question. I can help with appointments, departments, and doctors."

    if "hi" in msg or "hello" in msg or "salam" in msg or "hey" in msg:
        return (
            "Hello. I am Medical Center Information Bot. "
            "Ask me about appointments, departments, doctors, location, or emergency contact."
        )

    if "appointment" in msg or "book" in msg or "schedule" in msg:
        methods = "\n".join(f"- {item}" for item in MEDICAL_INFO["appointment_methods"])
        return (
            f"Appointment hours: {MEDICAL_INFO['appointment_hours']}\n"
            f"Booking options:\n{methods}"
        )

    if "department" in msg or "specialty" in msg or "services" in msg:
        departments = ", ".join(MEDICAL_INFO["departments"])
        return f"Available departments are: {departments}."

    if "doctor" in msg or "consultant" in msg or "physician" in msg:
        return "Available doctors:\n" + format_doctor_list()

    if "cardiology" in msg or "heart" in msg:
        return "For Cardiology, you can consult Dr. Ayesha Khan (Mon, Wed, Fri)."

    if "neurology" in msg or "brain" in msg:
        return "For Neurology, you can consult Dr. Bilal Ahmed (Tue, Thu, Sat)."

    if "child" in msg or "kids" in msg or "pediatric" in msg:
        return "For child care, you can consult Dr. Sana Iqbal in Pediatrics."

    if "skin" in msg or "derma" in msg or "rash" in msg:
        return "For skin-related issues, please visit Dermatology. Dr. Hina Saleem is available on Wed, Thu, Sat."

    if "ortho" in msg or "bone" in msg:
        return "For bone and joint issues, Dr. Umar Farooq is available in Orthopedics."

    if "location" in msg or "address" in msg or "where" in msg:
        return f"Our location is: {MEDICAL_INFO['location']}."

    if "emergency" in msg or "urgent" in msg or "accident" in msg:
        return MEDICAL_INFO["emergency"]

    if "thank" in msg:
        return "You are welcome. Let me know if you need details about appointments, departments, or doctors."

    return (
        "Sorry, I could not fully understand that question. "
        "Please ask about appointments, departments, doctors, location, or emergency."
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    bot_reply = get_bot_reply(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
