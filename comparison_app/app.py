import difflib

from flask import Flask, render_template, request

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


def build_report(house_row):
    (
        your_loc, your_assessment, your_yr_blt, your_living_area,
        your_style, your_bpg,
        fig1, fig1text, fig2, fig2text, fig3, fig3text, analysis_text,
    ) = main_program(house_row)
    return render_template(
        "report.html",
        your_loc=your_loc,
        your_assessment=f"{int(round(your_assessment)):,}",
        your_yr_blt=your_yr_blt,
        your_living_area=f"{int(your_living_area):,}",
        your_style=your_style,
        your_bpg=your_bpg,
        fig1=fig1.to_html(full_html=False),
        fig1text=fig1text,
        fig2=fig2.to_html(full_html=False),
        fig2text=fig2text,
        fig3=fig3.to_html(full_html=False),
        fig3text=fig3text,
        analysis_text=analysis_text,
        github_url=GITHUB_URL,
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
            submitted=address.strip(),
        )
    return render_template(
        "index.html",
        examples=EXAMPLE_ADDRESSES,
        github_url=GITHUB_URL,
    )


if __name__ == "__main__":
    app.run(debug=True)
