import difflib

from flask import Flask, jsonify, render_template, request

from compare_assessments import df, main_program

app = Flask(__name__)

GITHUB_URL = "https://github.com/niti-go/lexington-property-analysis"
EXAMPLE_ADDRESSES = ["1 AARON RD", "2 BACON ST", "3 DUDLEY RD"]
ALL_ADDRESSES = sorted(df["Location"].dropna().unique().tolist())


def find_matches(query, limit=5):
    """Return (exact_match_row, suggestions) for a user-typed address."""
    query = query.strip().upper()
    if not query:
        return None, []
    exact = df[df["Location"] == query]
    if not exact.empty:
        return exact.iloc[0], []
    suggestions = difflib.get_close_matches(query, ALL_ADDRESSES, n=limit, cutoff=0.5)
    return None, suggestions


def _short_dollars(amount):
    """Formats a dollar amount compactly: 2,430,000 -> $2.4M, 840,000 -> $840K."""
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    if amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    return f"${amount}"


def build_sparkline(history):
    """Converts a list of {year, total} points into SVG coordinates
    on a 100x40 viewBox, plus labeled points for the template to render."""
    if not history or len(history) < 2:
        return None
    totals = [h["total"] for h in history]
    lo, hi = min(totals), max(totals)
    span = hi - lo or 1  # avoid div-by-zero for flat series
    n = len(history)
    points = []
    for i, h in enumerate(history):
        x = round(i / (n - 1) * 100, 2)
        y = round(40 - (h["total"] - lo) / span * 32 - 4, 2)  # 4px padding top/bottom
        points.append({
            "x": x, "y": y,
            "year": h["year"],
            "total": h["total"],
            "total_formatted": f"${h['total']:,}",
            "total_short": _short_dollars(h["total"]),
        })
    return {
        "points": points,
        "path": " ".join(
            ("M" if i == 0 else "L") + f"{p['x']},{p['y']}"
            for i, p in enumerate(points)
        ),
        "last": points[-1],
    }


def build_report(house_row):
    r = main_program(house_row)
    verdict = r["verdict"]
    verdict["median_similar_formatted"] = f"{verdict['median_similar']:,}"
    comparables = [
        {**c, "sale_price_formatted": f"{c['sale_price']:,}",
         "living_area_formatted": f"{c['living_area']:,}",
         "assessment_formatted": f"{c['assessment']:,}"}
        for c in r["comparables"]
    ]
    sparkline = build_sparkline(r["valuation_history"])
    return render_template(
        "report.html",
        github_url=GITHUB_URL,
        your_loc=r["your_loc"],
        your_assessment=f"{int(round(r['your_assessment'])):,}",
        your_yr_blt=r["your_yr_blt"],
        your_living_area=f"{int(r['your_living_area']):,}",
        your_style=r["your_style"],
        your_bpg=r["your_bpg"],
        fig1=r["fig1"].to_html(full_html=False),
        fig1text=r["fig1text"],
        fig2=r["fig2"].to_html(full_html=False),
        fig2text=r["fig2text"],
        fig3=r["fig3"].to_html(full_html=False),
        fig3text=r["fig3text"],
        analysis_text=r["analysis_text"],
        verdict=verdict,
        comparables=comparables,
        sparkline=sparkline,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        address = request.form.get("address", "")
        match, suggestions = find_matches(address)
        if match is not None:
            return build_report(match)
        error = f"Couldn't find '{address.strip()}'."
        if suggestions:
            error += " Did you mean one of these?"
        else:
            error += " Try one of the examples below."
        return render_template(
            "index.html",
            error=error,
            suggestions=suggestions,
            examples=EXAMPLE_ADDRESSES,
            github_url=GITHUB_URL,
            submitted=address.strip().upper(),
        )
    return render_template(
        "index.html",
        examples=EXAMPLE_ADDRESSES,
        github_url=GITHUB_URL,
    )


@app.route("/suggest")
def suggest():
    q = request.args.get("q", "").strip().upper()
    if len(q) < 2:
        return jsonify([])
    prefix = [a for a in ALL_ADDRESSES if a.startswith(q)][:8]
    if len(prefix) >= 8:
        return jsonify(prefix)
    substring = [a for a in ALL_ADDRESSES if q in a and a not in prefix][:8 - len(prefix)]
    return jsonify(prefix + substring)


if __name__ == "__main__":
    app.run(debug=True)
