from flask import Flask, render_template, request
from compare_assessments import df, main_program

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        address = request.form.get("address", "").strip().upper()
        house_row = df[df["Location"] == address]
        if house_row.empty:
            return render_template(
                "index.html",
                error=f"Address '{address}' not found. Try the format: 123 MAIN ST",
            )
        (
            your_loc, your_assessment, your_yr_blt, your_living_area,
            your_style, your_bpg,
            fig1, fig1text, fig2, fig2text, fig3, fig3text, analysis_text,
        ) = main_program(house_row.iloc[0])
        return render_template(
            "report.html",
            your_loc=your_loc,
            your_assessment=f"{your_assessment:,.2f}",
            your_yr_blt=your_yr_blt,
            your_living_area=your_living_area,
            your_style=your_style,
            your_bpg=your_bpg,
            fig1=fig1.to_html(full_html=False),
            fig1text=fig1text,
            fig2=fig2.to_html(full_html=False),
            fig2text=fig2text,
            fig3=fig3.to_html(full_html=False),
            fig3text=fig3text,
            analysis_text=analysis_text,
        )
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
