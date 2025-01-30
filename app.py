gllvvaefrom flask import Flask, request, redirect, render_template
import sqlite3
import hashlib

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_code TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

init_db()

# Generate a short code
def generate_short_code(url):
    # Use SHA-256 hash to generate a unique code
    hash_object = hashlib.sha256(url.encode())
    hex_dig = hash_object.hexdigest()
    # Take the first 8 characters as the short code
    return hex_dig[:8]

# Home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url:
            return "Please enter a URL", 400

        # Generate short code
        short_code = generate_short_code(original_url)

        # Save to database
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                      (original_url, short_code))
            conn.commit()
        except sqlite3.IntegrityError:
            # If short code already exists, fetch the existing one
            c.execute("SELECT short_code FROM urls WHERE original_url = ?", (original_url,))
            short_code = c.fetchone()[0]
        conn.close()

        # Return the short URL
        short_url = request.host_url + short_code
        return f"Short URL: <a href='{short_url}'>{short_url}</a>"

    return render_template('index.html')

# Redirect to the original URL
@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = sqlite3.connect('url_shortener.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)