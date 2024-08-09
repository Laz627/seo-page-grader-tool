import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import os
from docx import Document

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the SEO factors with criteria, explanations, and weights
seo_factors = {
    "On-Page": {
        "H1 Tag": {
            "criteria": [
                ("Is Included On-Page At Top Of Heading Hierarchy", 10),
                ("Contains Proper Length", 8),
                ("Contains Primary Keyword", 9),
                ("There Is Only A Single H1 Tag On-Page", 8)
            ]
        },
        "Meta Title": {
            "criteria": [
                ("Contains Proper Length", 9),
                ("Contains Primary Keyword", 10),
                ("There Is Only A Single Meta Title On-Page", 8)
            ]
        },
        "Meta Description": {
            "criteria": [
                ("Contains Proper Length", 5),
                ("Contains Primary Keyword", 6),
                ("There Is Only A Single Meta Description On-Page", 4),
                ("Adequately Describes The Purpose Of The Page As A CTA", 5)
            ]
        },
        "Proper Heading Hierarchy": {
            "criteria": [
                ("Only A Single H1; H2s follow H1 tag; H3s follow H2s, etc…", 7)
            ]
        },
        "Image Alt Text": {
            "criteria": [
                ("Images Include Alt Text With Target Keyword", 3),
                ("Alt Text Properly Describes Imagery In A Meaningful Way", 2)
            ]
        },
        "Schema Markup": {
            "criteria": [
                ("Schema Is Included On-Page As JSON-LD", 9),
                ("No Errors Or Warnings With Schema Markup", 8),
                ("Schema Markup Matches Page Intent", 9)
            ]
        },
        "Internal Linking": {
            "criteria": [
                ("Other Pages Properly Point To This One With Target Keyword Included In Anchor Text", 7),
                ("This Page Logically Drives Users To The Next Anticipated Step In The User Journey", 6),
                ("This Page Doesn’t Send Users To A Dead End Experience / Poor Off-Ramp", 5)
            ]
        },
        "User Engagement Metrics": {
            "criteria": [
                ("Bounce Rate Meets or Exceeds Baseline", 8),
                ("Time Spent On-Page Meets or Exceeds Baseline", 9),
                ("CTR / Average KW Position Meets or Exceeds Baseline", 8),
                ("Visits Meet or Exceed Baseline", 7),
                ("Conversions / Abandons Meet or Exceed Baseline", 8),
                ("Scroll Depth Meets or Exceeds Baseline", 6)
            ]
        },
        "Primary Topic/Keyword Targeting": {
            "criteria": [
                ("Keyword Is Included Above The Fold In Content", 10),
                ("Relevant Secondary Keywords Are Included Within Subheads / Body Copy Of Page", 7),
                ("Page Matches Expected Keyword Intent", 9)
            ]
        },
        "URL Slug": {
            "criteria": [
                ("Short Length", 3),
                ("Omission of Stop Words", 2),
                ("Aligns With Informational Architecture Of Domain", 4),
                ("Lowercase only", 2),
                ("Hyphens only", 2),
                ("Non-parameterized (optional)", 1),
                ("ASCII characters only", 1),
                ("Depth of 5 or less from the homepage", 2)
            ]
        },
        "Quality of Content": {
            "criteria": [
                ("Accuracy", 10),
                ("Originality", 9),
                ("Tone Of Voice Matches Brand Standards", 8),
                ("Topic Completeness", 10),
                ("Readability", 8),
                ("Formatting (paragraph breaks, logical subheading structure)", 7),
                ("Content Freshness / Regularly Updated", 9),
                ("Page Matches Expected User Intent", 10),
                ("Other Pages Don't Cannibalize This One For Content", 8)
            ]
        }
    },
    "Off-Page": {
        "Page Authority vs Top 10": {
            "criteria": [
                ("Page Authority Is Greater Than Average Of Top 10 Results", 7)
            ]
        },
        "Page Authority vs Top 3": {
            "criteria": [
                ("Page Authority Is Greater Than Average Of Top 3 Results", 9)
            ]
        },
        "Backlinks from Relevant Domains": {
            "criteria": [
                ("Backlinks Are From Topically Relevant Domains", 7)
            ]
        },
        "Backlink Placement": {
            "criteria": [
                ("Backlinks Are Placed Higher Up On Sourced Pages / Are Likely To Be Clicked", 3)
            ]
        },
        "Backlink Anchor Text": {
            "criteria": [
                ("Backlinks Contain Topically Relevant Anchor Text", 6)
            ]
        },
        "Backlink Traffic": {
            "criteria": [
                ("Backlinks Are Placed On Pages That Actually Drive Visits", 7)
            ]
        }
    },
    "Technical": {
        "Canonical Tag": {
            "criteria": [
                ("Canonical Tag Contains Self-Reference", 6)
            ]
        },
        "Hreflang Tag": {
            "criteria": [
                ("Hreflang Tag (Optional) Is Correct, Targets The Right Locations, And References Other Translated Page Equivalents", 6)
            ]
        },
        "Indexability": {
            "criteria": [
                ("Page Is Indexable By Search Engines / Isn’t Blocked By Meta Tags Or Robots.txt", 10)
            ]
        },
        "Sitemap Inclusion": {
            "criteria": [
                ("Page Is Included In Sitemap.xml file", 2)
            ]
        },
        "Page Orphan Status": {
            "criteria": [
                ("Page Isn’t Orphaned", 2)
            ]
        },
        "Renderability": {
            "criteria": [
                ("Page Elements Are Renderable By Search Engines", 6)
            ]
        },
        "Web Core Vitals": {
            "criteria": [
                ("Page Passes Web Core Vitals Metrics / Exceeds Industry Average", 3)
            ]
        }
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
    for i, (criterion, weight) in enumerate(criteria):
        responses[criterion] = {
            "response": st.radio(criterion, ["Yes", "No"], index=1, key=f"{factor}_{i}"),
            "weight": weight
        }
    return responses

def calculate_score(inputs):
    score = 0
    max_score = 0
    for criterion, data in inputs.items():
        if data["response"] == "Yes":
            score += data["weight"]
        max_score += data["weight"]
    return (score / max_score) * 10 if max_score > 0 else 0

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
            for criterion, data in inputs[bucket][factor].items():
                doc.add_paragraph(f"{criterion}: {data['response']} (Weight: {data['weight']})")

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
        for factor, data in factors.items():
            bucket_inputs[factor] = get_user_input(factor, data["criteria"])
        inputs[bucket] = bucket_inputs

    if st.sidebar.button("Calculate Score"):
        scores = {}
        for bucket, factors in seo_factors.items():
            bucket_score = 0
            for factor in factors.keys():
                bucket_score += calculate_score(inputs[bucket][factor])
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
