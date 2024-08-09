import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import os
from docx import Document

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the SEO factors with criteria and explanations
seo_factors = {
    "On-Page": {
        "H1 Tag": [
            "Is Included On-Page At Top Of Heading Hierarchy",
            "Contains Proper Length",
            "Contains Primary Keyword",
            "There Is Only A Single H1 Tag On-Page"
        ],
        "Meta Title": [
            "Contains Proper Length",
            "Contains Primary Keyword",
            "There Is Only A Single Meta Title On-Page"
        ],
        "Meta Description": [
            "Contains Proper Length",
            "Contains Primary Keyword",
            "There Is Only A Single Meta Description On-Page",
            "Adequately Describes The Purpose Of The Page As A CTA"
        ],
        "Proper Heading Hierarchy": [
            "Only A Single H1; H2s follow H1 tag; H3s follow H2s, etc…"
        ],
        "Image Alt Text": [
            "Images Include Alt Text With Target Keyword",
            "Alt Text Properly Describes Imagery In A Meaningful Way"
        ],
        "Schema Markup": [
            "Schema Is Included On-Page As JSON-LD",
            "No Errors Or Warnings With Schema Markup",
            "Schema Markup Matches Page Intent"
        ],
        "Internal Linking": [
            "Other Pages Properly Point To This One With Target Keyword Included In Anchor Text",
            "This Page Logically Drives Users To The Next Anticipated Step In The User Journey",
            "This Page Doesn’t Send Users To A Dead End Experience / Poor Off-Ramp"
        ],
        "User Engagement Metrics": [
            "Bounce Rate Meets or Exceeds Baseline",
            "Time Spent On-Page Meets or Exceeds Baseline",
            "CTR / Average KW Position Meets or Exceeds Baseline",
            "Visits Meet or Exceed Baseline",
            "Conversions / Abandons Meet or Exceed Baseline",
            "Scroll Depth Meets or Exceeds Baseline"
        ],
        "Primary Topic/Keyword Targeting": [
            "Keyword Is Included Above The Fold In Content",
            "Relevant Secondary Keywords Are Included Within Subheads / Body Copy Of Page",
            "Page Matches Expected Keyword Intent"
        ],
        "URL Slug": [
            "Short Length",
            "Omission of Stop Words",
            "Aligns With Informational Architecture Of Domain",
            "Lowercase only",
            "Hyphens only",
            "Non-parameterized (optional)",
            "ASCII characters only",
            "Depth of 5 or less from the homepage"
        ],
        "Quality of Content": [
            "Accuracy",
            "Originality",
            "Tone Of Voice Matches Brand Standards",
            "Topic Completeness",
            "Readability",
            "Formatting (paragraph breaks, logical subheading structure)",
            "Content Freshness / Regularly Updated",
            "Page Matches Expected User Intent",
            "Other Pages Don't Cannibalize This One For Content"
        ]
    },
    "Off-Page": {
        "Page Authority vs Top 10": [
            "Page Authority Is Greater Than Average Of Top 10 Results"
        ],
        "Page Authority vs Top 3": [
            "Page Authority Is Greater Than Average Of Top 3 Results"
        ],
        "Backlinks from Relevant Domains": [
            "Backlinks Are From Topically Relevant Domains"
        ],
        "Backlink Placement": [
            "Backlinks Are Placed Higher Up On Sourced Pages / Are Likely To Be Clicked"
        ],
        "Backlink Anchor Text": [
            "Backlinks Contain Topically Relevant Anchor Text"
        ],
        "Backlink Traffic": [
            "Backlinks Are Placed On Pages That Actually Drive Visits"
        ]
    },
    "Technical": {
        "Canonical Tag": [
            "Canonical Tag Contains Self-Reference"
        ],
        "Hreflang Tag": [
            "Hreflang Tag (Optional) Is Correct, Targets The Right Locations, And References Other Translated Page Equivalents"
        ],
        "Indexability": [
            "Page Is Indexable By Search Engines / Isn’t Blocked By Meta Tags Or Robots.txt"
        ],
        "Sitemap Inclusion": [
            "Page Is Included In Sitemap.xml file"
        ],
        "Page Orphan Status": [
            "Page Isn’t Orphaned"
        ],
        "Renderability": [
            "Page Elements Are Renderable By Search Engines"
        ],
        "Web Core Vitals": [
            "Page Passes Web Core Vitals Metrics / Exceeds Industry Average"
        ]
    }
}

# Calculate bucket weights
bucket_weights = {
    "On-Page": 0.55,
    "Off-Page": 0.30,
    "Technical": 0.15
}

def get_user_input(factor, criteria):
    responses = {}
    st.subheader(factor)
    for criterion in criteria:
        responses[criterion] = st.radio(criterion, ["Yes", "No"], index=1)
    return responses

def calculate_score(inputs, factors):
    score = 0
    max_score = len(inputs)
    for criterion, response in inputs.items():
        if response == "Yes":
            score += 1
    return (score / max_score) * 10

def get_gpt4_recommendations(inputs):
    prompt = f"Based on the following SEO audit results, provide recommendations for improvement:\n\n{inputs}\n\nPlease provide specific, actionable recommendations for each area that needs improvement."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an SEO expert providing recommendations based on an audit."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def export_to_word(inputs, scores, recommendations):
    doc = Document()
    doc.add_heading('SEO Audit Results', 0)

    for bucket, factors in seo_factors.items():
        doc.add_heading(f"{bucket} Factors", level=1)
        for factor, criteria in factors.items():
            doc.add_heading(factor, level=2)
            for criterion, response in inputs[factor].items():
                doc.add_paragraph(f"{criterion}: {response}")

    doc.add_heading('Scores', level=1)
    for bucket, score in scores.items():
        doc.add_paragraph(f"{bucket}: {score:.2f}/10")
    doc.add_paragraph(f"Overall Score: {scores['Overall']:.2f}/10")

    doc.add_heading('Recommendations', level=1)
    doc.add_paragraph(recommendations)

    doc.save('seo_audit_results.docx')

def main():
    st.title("SEO Ranking Likelihood Calculator")

    inputs = {}
    for bucket, factors in seo_factors.items():
        st.sidebar.subheader(bucket)
        bucket_inputs = {}
        for factor, criteria in factors.items():
            bucket_inputs[factor] = get_user_input(factor, criteria)
        inputs[bucket] = bucket_inputs

    if st.sidebar.button("Calculate Score"):
        scores = {}
        for bucket, factors in seo_factors.items():
            bucket_score = 0
            for factor in factors.keys():
                bucket_score += calculate_score(inputs[bucket][factor], factors[factor])
            scores[bucket] = (bucket_score / len(factors)) * 10

        overall_score = sum(score * bucket_weights[bucket] for bucket, score in scores.items())
        scores["Overall"] = overall_score

        st.subheader("SEO Scores")
        for bucket, score in scores.items():
            st.write(f"{bucket}: {score:.2f}/10")

        fig, ax = plt.subplots()
        ax.bar(scores.keys(), scores.values())
        ax.set_ylim(0, 10)
        ax.set_ylabel("Score")
        ax.set_title("SEO Scores by Category")
        st.pyplot(fig)

        recommendations = get_gpt4_recommendations(inputs)
        st.subheader("Recommendations")
        st.write(recommendations)

        export_to_word(inputs, scores, recommendations)
        st.success("Results exported to 'seo_audit_results.docx'")

if __name__ == "__main__":
    main()
