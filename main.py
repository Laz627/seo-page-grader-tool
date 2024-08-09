import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
import os
from docx import Document

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the SEO factors, their weights, and explanations
seo_factors = {
    "On-Page": {
        "H1 Tag": {
            "weight": 8,
            "explanation": "The main heading of the page. Should include the primary keyword and be unique."
        },
        "Meta Title": {
            "weight": 9,
            "explanation": "The title tag that appears in search results. Should be concise and include the primary keyword."
        },
        "Meta Description": {
            "weight": 5,
            "explanation": "A brief summary of the page content that appears in search results. Should include the primary keyword and act as a call-to-action."
        },
        "Proper Heading Hierarchy": {
            "weight": 7,
            "explanation": "Correct use of H1, H2, H3 tags in a logical structure."
        },
        "Image Alt Text": {
            "weight": 4,
            "explanation": "Descriptive text for images, including target keywords where appropriate."
        },
        "Schema Markup": {
            "weight": 8,
            "explanation": "Structured data that helps search engines understand the content of the page."
        },
        "Internal Linking": {
            "weight": 7,
            "explanation": "Links to and from other relevant pages on your website."
        },
        "User Engagement Metrics": {
            "weight": 9,
            "explanation": "Metrics like bounce rate, time on page, and CTR that indicate user satisfaction."
        },
        "Primary Topic/Keyword Targeting": {
            "weight": 9,
            "explanation": "Clear focus on a primary topic or keyword throughout the page content."
        },
        "URL Slug": {
            "weight": 5,
            "explanation": "The part of the URL that identifies the specific page. Should be short and include the primary keyword."
        },
        "Quality of Content": {
            "weight": 9,
            "explanation": "Well-written, original content that thoroughly covers the topic and matches user intent."
        }
    },
    "Off-Page": {
        "Page Authority vs Top 10": {
            "weight": 7,
            "explanation": "How your page's authority compares to the average of the top 10 search results."
        },
        "Page Authority vs Top 3": {
            "weight": 9,
            "explanation": "How your page's authority compares to the average of the top 3 search results."
        },
        "Backlinks from Relevant Domains": {
            "weight": 8,
            "explanation": "Links from other websites in your industry or niche."
        },
        "Backlink Placement": {
            "weight": 5,
            "explanation": "Where the backlinks appear on the linking pages. Higher placement is generally better."
        },
        "Backlink Anchor Text": {
            "weight": 7,
            "explanation": "The clickable text of the backlinks. Should include relevant keywords."
        },
        "Backlink Traffic": {
            "weight": 7,
            "explanation": "The amount of traffic the linking pages receive."
        }
    },
    "Technical": {
        "Canonical Tag": {
            "weight": 7,
            "explanation": "Specifies the preferred version of a page to search engines."
        },
        "Hreflang Tag": {
            "weight": 6,
            "explanation": "Tells search engines which language you're using on a specific page."
        },
        "Indexability": {
            "weight": 9,
            "explanation": "Whether search engines are allowed to index the page."
        },
        "Sitemap Inclusion": {
            "weight": 5,
            "explanation": "Whether the page is included in the website's XML sitemap."
        },
        "Page Orphan Status": {
            "weight": 5,
            "explanation": "Whether the page is linked to from other pages on the site."
        },
        "Renderability": {
            "weight": 7,
            "explanation": "Whether search engines can properly render and understand the page content."
        },
        "Web Core Vitals": {
            "weight": 6,
            "explanation": "Google's metrics for page experience, including loading performance, interactivity, and visual stability."
        }
    }
}

# Calculate bucket weights
bucket_weights = {
    "On-Page": 0.55,
    "Off-Page": 0.30,
    "Technical": 0.15
}

def get_user_input(factor, weight, explanation):
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        value = st.selectbox(f"{factor} (Weight: {weight})", ["Yes", "No", "N/A"], key=factor)
    with col2:
        st.help(explanation)
    return value

def calculate_score(inputs, factors):
    score = 0
    max_score = 0
    for factor, data in factors.items():
        if inputs[factor] == "Yes":
            score += data["weight"]
        if inputs[factor] != "N/A":
            max_score += data["weight"]
    return (score / max_score) * 10 if max_score > 0 else 0

def get_gpt4_recommendations(inputs):
    prompt = f"Based on the following SEO audit results, provide recommendations for improvement:\n\n{inputs}\n\nPlease provide specific, actionable recommendations for each area that needs improvement."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SEO expert providing recommendations based on an audit."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def export_to_word(inputs, scores, recommendations, export_details):
    doc = Document()
    doc.add_heading('SEO Audit Results', 0)

    for bucket, factors in seo_factors.items():
        doc.add_heading(f"{bucket} Factors", level=1)
        for factor, data in factors.items():
            doc.add_paragraph(f"{factor} (Weight: {data['weight']}): {inputs[factor]}")
            if factor in export_details:
                doc.add_paragraph(f"Details: {export_details[factor]}")

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
    export_details = {}
    for bucket, factors in seo_factors.items():
        st.sidebar.subheader(bucket)
        for factor, data in factors.items():
            inputs[factor] = get_user_input(factor, data["weight"], data["explanation"])
            if st.sidebar.checkbox(f"Add details for {factor}"):
                export_details[factor] = st.sidebar.text_area(f"{factor} details", key=f"{factor}_details")

    if st.sidebar.button("Calculate Score"):
        scores = {}
        for bucket, factors in seo_factors.items():
            bucket_score = calculate_score({k: inputs[k] for k in factors.keys()}, factors)
            scores[bucket] = bucket_score

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

        export_to_word(inputs, scores, recommendations, export_details)
        st.success("Results exported to 'seo_audit_results.docx'")

if __name__ == "__main__":
    main()
