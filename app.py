import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, Contact
import resend
from dotenv import load_dotenv

# ======================
# LOAD ENVIRONMENT VARIABLES
# ======================
load_dotenv()

app = Flask(__name__)

# ======================
# CONFIGURATION
# ======================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(BASE_DIR, "contact.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ======================
# INIT EXTENSIONS
# ======================
db.init_app(app)
migrate = Migrate(app, db)

# ======================
# CORS CONFIG
# ======================
# Only allow API routes; supports preflight and all methods
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# ======================
# RESEND CONFIG
# ======================
resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

# ======================
# ROUTES
# ======================

@app.route("/", methods=["GET"])
def home():
    return "API is running 🚀"


@app.route("/api/contact", methods=["POST"])
def create_contact():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    project_type = data.get("projectType")
    message = data.get("message")

    if not all([name, email, project_type, message]):
        return jsonify({"error": "All fields are required"}), 400

    # Save to DB
    new_contact = Contact(
        name=name,
        email=email,
        project_type=project_type,
        message=message
    )

    db.session.add(new_contact)
    db.session.commit()

    # Send email
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": TO_EMAIL,
            "subject": f"New Contact from {name}",
            "html": f"""
                <h2>New Contact Message</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Project Type:</strong> {project_type}</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
            """
        })
    except Exception as e:
        print("Email error:", e)

    return jsonify({"message": "Message sent successfully"}), 201


@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "project_type": c.project_type,
            "message": c.message,
            "created_at": c.created_at
        } for c in contacts
    ])


# ======================
# RUN (LOCAL ONLY)
# ======================
if __name__ == "__main__":
    # In Render, gunicorn will run this automatically
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))