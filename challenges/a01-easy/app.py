"""A01 easy: an intentionally vulnerable horizontal-IDOR training service.

The defect is deliberately isolated to ``get_record``: a valid access pass is
accepted for any record, rather than checking that the requested record belongs
to the authenticated student. Do not use this pattern in a real application.
"""

import os
import secrets

from flask import Flask, jsonify, render_template, request, session


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SESSION_SECRET") or secrets.token_urlsafe(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


def instance_flag() -> str:
    """Return the orchestrator-provided flag, with a safe standalone fallback."""
    configured_flag = os.environ.get("FLAG", "").strip()
    if configured_flag:
        return configured_flag
    return f"RTSA{{a01_idor_{secrets.token_urlsafe(18)}}}"


DYNAMIC_FLAG = instance_flag()

STUDENT_ACCOUNT = secrets.randbelow(900) + 100
EXECUTIVE_ACCOUNT = secrets.randbelow(900) + 100
while EXECUTIVE_ACCOUNT in {STUDENT_ACCOUNT, STUDENT_ACCOUNT - 1}:
    EXECUTIVE_ACCOUNT = secrets.randbelow(900) + 100

STUDENT = {
    "id": f"cadet-{STUDENT_ACCOUNT}",
    "name": "Academy Student Cadet",
    "role": "Student Trainee",
    "email": "cadet@redteamacademy.com",
    "access_level": "Tier-1",
    "account_num": STUDENT_ACCOUNT,
}


def documents() -> dict[str, dict[str, str]]:
    """Create records at startup so the protected value is never source-coded."""
    return {
        f"DOC-{STUDENT_ACCOUNT - 1}": {
            "title": "Welcome Pack & Student Rules",
            "author": "Student Administration",
            "category": "General",
            "owner": f"cadet-{STUDENT_ACCOUNT}",
            "content": "Welcome to RedTeam Hacker Academy. Follow training protocols strictly.",
        },
        f"DOC-{STUDENT_ACCOUNT}": {
            "title": "Lab Environment Getting Started",
            "author": "Cadet User",
            "category": "Courseware",
            "owner": f"cadet-{STUDENT_ACCOUNT}",
            "content": "Basic terminal usage, proxy setup, and lab orientation.",
        },
        f"DOC-{EXECUTIVE_ACCOUNT}": {
            "title": "Executive Clearance Dossier",
            "author": "Chief Security Director",
            "category": "Confidential",
            "owner": f"executive-{EXECUTIVE_ACCOUNT}",
            "content": "CLASSIFIED AUDIT DATA:\nExecutive vault access approved.\n"
            f"Flag: {DYNAMIC_FLAG}",
        },
    }


DOCUMENTS = documents()


@app.after_request
def add_response_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/")
def home():
    session.setdefault("student_id", STUDENT["id"])
    return render_template(
        "portal.html",
        user=STUDENT,
        account_num=STUDENT["account_num"],
        documents=[DOCUMENTS[doc_id] | {"id": doc_id} for doc_id in (f"DOC-{STUDENT_ACCOUNT - 1}", f"DOC-{STUDENT_ACCOUNT}")],
    )


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/api/v1/student/documents/<document_id>")
def get_record(document_id: str):
    """Return a document for the logged-in student.

    INTENTIONAL A01 FLAW: the session is authenticated, but the requested
    document's owner is never compared with the logged-in student's ID. This is
    a classic object-level authorization (IDOR) defect.
    """
    if not session.get("student_id"):
        return jsonify({"success": False, "error": "Authentication required."}), 401

    document = DOCUMENTS.get(document_id.upper())
    if document is None:
        return jsonify({"success": False, "error": "Record not found."}), 404

    return jsonify({
        "success": True,
        "account_number": STUDENT["account_num"],
        "document_id": document_id.upper(),
        "classification": document["category"],
        "title": document["title"],
        "author": document["author"],
        "content": document["content"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("LAB_PORT") or os.environ.get("PORT") or "6001"), debug=False)
