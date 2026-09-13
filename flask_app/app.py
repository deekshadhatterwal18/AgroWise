import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from .database import get_db_connection
from .weather_service import (
    geocode_location,
    get_weather_forecast,
    generate_farming_advisory
)
from ml.market_analysis.market_service import (
    get_all_commodities,
    get_states_for_commodity,
    get_state_price_comparison
)


load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "agrowise-development-secret"
)


# =========================================================
# GOVERNMENT SCHEMES (static list — shown on the landing page)
# =========================================================

GOVERNMENT_SCHEMES = [
    {
        "icon": "🌾",
        "name": "PM-KISAN",
        "description": (
            "Direct income support of ₹6,000 per year to "
            "eligible farmer families, paid in three "
            "installments."
        ),
        "link": "https://pmkisan.gov.in"
    },
    {
        "icon": "🛡️",
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "description": (
            "Crop insurance scheme that protects farmers "
            "against crop loss due to natural calamities, "
            "pests and diseases."
        ),
        "link": "https://pmfby.gov.in"
    },
    {
        "icon": "🧪",
        "name": "Soil Health Card Scheme",
        "description": (
            "Provides farmers with soil nutrient reports "
            "and crop-wise recommendations to improve soil "
            "fertility and productivity."
        ),
        "link": "https://soilhealth.dac.gov.in"
    },
    {
        "icon": "💳",
        "name": "Kisan Credit Card (KCC)",
        "description": (
            "Gives farmers timely access to short-term "
            "credit for crop production, at concessional "
            "interest rates."
        ),
        "link": "https://www.myscheme.gov.in/schemes/kcc"
    },
    {
        "icon": "👵",
        "name": "PM Kisan Maandhan Yojana",
        "description": (
            "A voluntary pension scheme offering ₹3,000 "
            "monthly pension to small and marginal farmers "
            "after the age of 60."
        ),
        "link": "https://maandhan.in"
    },
    {
        "icon": "🚜",
        "name": "Rashtriya Krishi Vikas Yojana (RKVY)",
        "description": (
            "State-level scheme supporting agricultural "
            "infrastructure, mechanization, and farmer "
            "income enhancement projects."
        ),
        "link": "https://rkvy.nic.in"
    },
]


@app.route("/")
def home():
    return render_template(
        "index.html",
        schemes=GOVERNMENT_SCHEMES
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    location = request.form.get("location", "").strip()

    if not name or not email or not password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("register"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("register"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            flash(
                "An account with this email already exists.",
                "error"
            )
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password_hash, location)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (
                name,
                email,
                password_hash,
                location
            )
        )

        cursor.fetchone()
        connection.commit()

        flash(
            "Registration successful! Please login.",
            "success"
        )

        return redirect(url_for("login"))

    except Exception as e:

        if connection:
            connection.rollback()

        print("Registration error:", e)

        flash(
            "Something went wrong. Please try again.",
            "error"
        )

        return redirect(url_for("register"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN - "smart redirect" ke saath: jahan se aaye
# the login ke baad wahi wapas jaayenge, dashboard pe force nahi
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        next_page = request.args.get("next", "")
        return render_template("login.html", next=next_page)

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    next_page = request.form.get("next", "")

    if not email or not password:
        flash(
            "Please enter email and password.",
            "error"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, email, password_hash, location
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            flash(
                "Invalid email or password.",
                "error"
            )
            return redirect(url_for("login"))

        user_id, name, user_email, password_hash, location = user

        if not check_password_hash(
            password_hash,
            password
        ):
            flash(
                "Invalid email or password.",
                "error"
            )
            return redirect(url_for("login"))

        session["user_id"] = user_id
        session["name"] = name
        session["email"] = user_email
        session["location"] = location

        flash(
            f"Welcome back, {name}!",
            "success"
        )

        # jahan se aaye the wahi bhejo, agar "next" nahi hai
        # to home page pe jao (landing page ka dashboard)
        if next_page:
            return redirect(next_page)
        return redirect(url_for("home"))

    except Exception as e:

        print("Login error:", e)

        flash(
            "Something went wrong. Please try again.",
            "error"
        )

        return redirect(url_for("login"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DASHBOARD
# ---------------------------------------------------------
# FIX: pehle ye "dashboard.html" (alag/duplicate dashboard)
# render karta tha. Ab sirf landing page ("home") par
# redirect karta hai, jahan login ke baad wahi asli
# dashboard UI already dikhta hai. Isse jitni bhi jagah
# url_for('dashboard') use hota hai (jaise chatbot widget
# ka "Dashboard" link), wo sab ab sahi jagah pahunchenge.
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    return redirect(url_for("home"))


# =========================================================
# DISEASE DETECTION
# =========================================================

@app.route("/disease-detection")
def disease_detection():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    return render_template("disease.html")


@app.route(
    "/api/disease/predict",
    methods=["POST"]
)
def disease_predict():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "error": "No image uploaded."
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "success": False,
            "error": "Please select an image."
        }), 400

    allowed_extensions = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    extension = image.filename.rsplit(
        ".",
        1
    )[-1].lower()

    if extension not in allowed_extensions:
        return jsonify({
            "success": False,
            "error": (
                "Only JPG, JPEG, PNG and WEBP "
                "images are allowed."
            )
        }), 400

    try:

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        upload_folder = os.path.join(
            base_dir,
            "ml",
            "disease_detection",
            "uploads"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        image_path = os.path.join(
            upload_folder,
            "uploaded_leaf." + extension
        )

        image.save(image_path)

        from ml.disease_detection.predict import predict

        result = predict(image_path)

        return jsonify(result)

    except Exception as e:

        print(
            "Disease prediction error:",
            e
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# WEATHER FORECAST
# =========================================================

@app.route("/weather")
def weather_page():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    return render_template(
        "weather.html",
        default_location=session.get("location", "")
    )


@app.route("/api/weather", methods=["GET"])
def weather_api():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    location_query = request.args.get("location", "").strip()

    if not location_query:
        location_query = session.get("location", "")

    if not location_query:
        return jsonify({
            "success": False,
            "error": (
                "Please enter a location "
                "(city, district or village)."
            )
        }), 400

    place = geocode_location(location_query)

    if not place:
        return jsonify({
            "success": False,
            "error": (
                f"Could not find location '{location_query}'. "
                "Try a nearby city name."
            )
        }), 404

    weather_data = get_weather_forecast(
        place["latitude"],
        place["longitude"]
    )

    if not weather_data:
        return jsonify({
            "success": False,
            "error": "Could not fetch weather data. Try again later."
        }), 502

    advisory = generate_farming_advisory(weather_data)

    return jsonify({
        "success": True,
        "location": place,
        "current": weather_data["current"],
        "forecast": weather_data["forecast"],
        "advisory": advisory
    })


# =========================================================
# MARKET ANALYSIS
# =========================================================

@app.route("/market")
def market_page():

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    return render_template("market.html")


@app.route("/api/market/commodities", methods=["GET"])
def market_commodities_api():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    commodities = get_all_commodities()

    return jsonify({
        "success": True,
        "commodities": commodities
    })


@app.route("/api/market/states", methods=["GET"])
def market_states_api():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    commodity = request.args.get("commodity", "").strip()

    if not commodity:
        return jsonify({
            "success": False,
            "error": "Please select a crop first."
        }), 400

    states = get_states_for_commodity(commodity)

    return jsonify({
        "success": True,
        "states": states
    })


@app.route("/api/market/prices", methods=["GET"])
def market_prices_api():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    commodity = request.args.get("commodity", "").strip()

    if not commodity:
        return jsonify({
            "success": False,
            "error": "Please select a crop."
        }), 400

    result = get_state_price_comparison(commodity)

    if not result:
        return jsonify({
            "success": False,
            "error": "No price data found for this crop."
        }), 404

    return jsonify({
        "success": True,
        "summary": result["summary"],
        "state_prices": result["state_prices"]
    })


# =========================================================
# FARMER CONNECT (community forum)
# =========================================================

@app.route("/farmer-connect")
def farmer_connect():
    """
    Feed page: shows all posts, newest first, with each
    post's author name and comment count.
    """

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                posts.id,
                posts.title,
                posts.content,
                posts.created_at,
                users.name AS author_name,
                COUNT(comments.id) AS comment_count
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN comments ON comments.post_id = posts.id
            GROUP BY posts.id, users.name
            ORDER BY posts.created_at DESC;
            """
        )

        posts = cursor.fetchall()

    except Exception as e:

        print("Farmer Connect feed error:", e)
        posts = []
        flash("Could not load posts right now.", "error")

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "farmer_connect.html",
        posts=posts
    )


@app.route("/farmer-connect/new", methods=["GET", "POST"])
def new_post():
    """Form to create a new post."""

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    if request.method == "GET":
        return render_template("new_post.html")

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        flash("Please fill in both title and content.", "error")
        return redirect(url_for("new_post"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO posts (user_id, title, content)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (
                session["user_id"],
                title,
                content
            )
        )

        new_post_id = cursor.fetchone()[0]
        connection.commit()

        flash("Your post has been shared!", "success")

        return redirect(url_for("view_post", post_id=new_post_id))

    except Exception as e:

        if connection:
            connection.rollback()

        print("Create post error:", e)

        flash("Could not create your post. Please try again.", "error")

        return redirect(url_for("new_post"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/farmer-connect/<int:post_id>")
def view_post(post_id):
    """Shows one post in full, with all its comments."""

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                posts.id,
                posts.title,
                posts.content,
                posts.created_at,
                users.name AS author_name
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.id = %s;
            """,
            (post_id,)
        )

        post = cursor.fetchone()

        if not post:
            flash("Post not found.", "error")
            return redirect(url_for("farmer_connect"))

        cursor.execute(
            """
            SELECT
                comments.content,
                comments.created_at,
                users.name AS author_name
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at ASC;
            """,
            (post_id,)
        )

        comments = cursor.fetchall()

    except Exception as e:

        print("View post error:", e)
        flash("Could not load this post.", "error")
        return redirect(url_for("farmer_connect"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "post_detail.html",
        post=post,
        comments=comments
    )


@app.route("/farmer-connect/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    """Adds a comment to a post, then redirects back to it."""

    if "user_id" not in session:
        flash(
            "Please login first.",
            "error"
        )
        return redirect(url_for("login", next=request.path))

    content = request.form.get("content", "").strip()

    if not content:
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("view_post", post_id=post_id))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO comments (post_id, user_id, content)
            VALUES (%s, %s, %s);
            """,
            (
                post_id,
                session["user_id"],
                content
            )
        )

        connection.commit()

    except Exception as e:

        if connection:
            connection.rollback()

        print("Add comment error:", e)

        flash("Could not add your comment.", "error")

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(url_for("view_post", post_id=post_id))


# =========================================================
# CROP RECOMMENDATION
# =========================================================

@app.route("/crop-recommendation")
def crop_recommendation():

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login", next=request.path))

    return render_template("crop.html")


@app.route("/api/crop/predict", methods=["POST"])
def crop_predict():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:
        data = request.get_json()

        from ml.crop_recommendation.predict import predict_crop

        result = predict_crop(
            N=float(data.get("N")),
            P=float(data.get("P")),
            K=float(data.get("K")),
            temperature=float(data.get("temperature")),
            humidity=float(data.get("humidity")),
            ph=float(data.get("ph")),
            rainfall=float(data.get("rainfall")),
        )

        return jsonify({
            "success": True,
            "recommended_crop": result["recommended_crop"],
            "top_predictions": result["top_predictions"]
        })

    except Exception as e:
        print("Crop prediction error:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# YIELD PREDICTION
# =========================================================

@app.route("/yield-prediction")
def yield_prediction():

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login", next=request.path))

    from ml.yield_prediction.predict import get_dropdown_options

    options = get_dropdown_options()

    return render_template(
        "yield.html",
        crops=options["crops"],
        seasons=options["seasons"],
        states=options["states"]
    )


@app.route("/api/yield/predict", methods=["POST"])
def yield_predict():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:
        data = request.get_json()

        from ml.yield_prediction.predict import predict_yield

        result = predict_yield(data)

        return jsonify({
            "success": True,
            "predicted_yield": result
        })

    except Exception as e:
        print("Yield prediction error:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# RAG CHATBOT
# =========================================================

@app.route("/chatbot")
def chatbot_page():

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login", next=request.path))

    return render_template("chatbot.html")


@app.route("/api/chatbot/ask", methods=["POST"])
def chatbot_ask():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "Please enter a question."
            }), 400

        from ml.rag_chatbot.generator import generate_answer

        result = generate_answer(question, top_k=8)

        return jsonify({
            "success": True,
            "answer": result["answer"],
            "sources": result["sources"],
            "num_chunks_used": result["num_chunks_used"]
        })

    except Exception as e:
        print("Chatbot error:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
