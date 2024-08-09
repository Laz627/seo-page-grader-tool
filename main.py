import streamlit as st
import pandas as pd
import openai
import os
from docx import Document

# Set up the OpenAI API key prompt
st.sidebar.title("Setup")
openai_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

# Define the SEO factors with criteria and weights
seo_factors = {
    "On-Page": {
        "H1 Tag": {
            "criteria": [
                ("Is Included On-Page At Top Of Heading Hierarchy", 10, "The H1 tag is the main heading of the page. It should include the primary keyword and be unique, as it signals to search engines and users what the page is about."),
                ("Contains Proper Length", 8, "The H1 tag should be of appropriate length to ensure clarity and relevance."),
                ("Contains Primary Keyword", 9, "Including the primary keyword in the H1 tag helps with search engine indexing and ranking."),
                ("There Is Only A Single H1 Tag On-Page", 8, "Having only one H1 tag ensures clarity in the page's structure and prevents confusion for search engines.")
            ]
        },
        "Meta Title": {
            "criteria": [
                ("Contains Proper Length", 9, "The meta title should be concise and to the point, making it easy for users and search engines to understand."),
                ("Contains Primary Keyword", 10, "Including the primary keyword in the meta title helps search engines index the page."),
                ("There Is Only A Single Meta Title On-Page", 8, "Having a single meta title avoids confusion and ensures that the page is properly indexed.")
            ]
        },
        "Meta Description": {
            "criteria": [
                ("Contains Proper Length", 5, "A meta description of proper length ensures that the summary is clear and complete."),
                ("Contains Primary Keyword", 6, "Including the primary keyword in the meta description helps search engines understand the page content."),
                ("There Is Only A Single Meta Description On-Page", 4, "A single meta description prevents duplicate content issues."),
                ("Adequately Describes The Purpose Of The Page As A CTA", 5, "A meta description that acts as a call-to-action can improve click-through rates.")
            ]
        },
        "Proper Heading Hierarchy": {
            "criteria": [
                ("Only A Single H1; H2s follow H1 tag; H3s follow H2s, etc…", 7, "Proper use of heading tags (H1, H2, H3) helps search engines understand the structure and importance of content.")
            ]
        },
        "Image Alt Text": {
            "criteria": [
                ("Images Include Alt Text With Target Keyword", 3, "Alt text provides a description of images, helping search engines index them and improving accessibility for users with visual impairments."),
                ("Alt Text Properly Describes Imagery In A Meaningful Way", 2, "Alt text should meaningfully describe the imagery to provide context to search engines and users.")
            ]
        },
        "Schema Markup": {
            "criteria": [
                ("Schema Is Included On-Page As JSON-LD", 9, "Structured data in JSON-LD format helps search engines understand the content of the page better, improving the chances of rich results."),
                ("No Errors Or Warnings With Schema Markup", 8, "Ensuring schema markup has no errors improves the likelihood of enhanced search result features."),
                ("Schema Markup Matches Page Intent", 9, "Schema markup should align with the page’s content and purpose to enhance search visibility.")
            ]
        },
        "Internal Linking": {
            "criteria": [
                ("Other Pages Properly Point To This One With Target Keyword Included In Anchor Text", 7, "Proper internal linking helps users and search engines navigate your site more effectively, passing authority between pages."),
                ("This Page Logically Drives Users To The Next Anticipated Step In The User Journey", 6, "Internal links should guide users through a logical flow on your website."),
                ("This Page Doesn’t Send Users To A Dead End Experience / Poor Off-Ramp", 5, "Avoiding dead-end pages ensures a better user experience and keeps users engaged.")
            ]
        },
        "User Engagement Metrics": {
            "criteria": [
                ("Bounce Rate Meets or Exceeds Baseline", 8, "A lower bounce rate indicates that users find the content relevant and are more likely to stay on the page."),
                ("Time Spent On-Page Meets or Exceeds Baseline", 9, "More time spent on the page suggests users are engaged with the content."),
                ("CTR / Average KW Position Meets or Exceeds Baseline", 8, "A higher click-through rate and better average keyword position indicate that the page is well-optimized for search."),
                ("Visits Meet or Exceed Baseline", 7, "Higher visit numbers suggest that the page is attracting a significant amount of traffic."),
                ("Conversions / Abandons Meet or Exceed Baseline", 8, "A higher conversion rate with fewer abandons shows that the page effectively meets user intent."),
                ("Scroll Depth Meets or Exceeds Baseline", 6, "Greater scroll depth indicates that users are consuming more content on the page.")
            ]
        },
        "Primary Topic/Keyword Targeting": {
            "criteria": [
                ("Keyword Is Included Above The Fold In Content", 10, "Placing the primary keyword above the fold ensures it is one of the first things users and search engines see."),
                ("Relevant Secondary Keywords Are Included Within Subheads / Body Copy Of Page", 7, "Incorporating secondary keywords throughout the content helps to enhance relevance and rank for multiple search terms."),
                ("Page Matches Expected Keyword Intent", 9, "Matching the content to the expected intent behind the keywords improves user satisfaction and ranking potential.")
            ]
        },
        "URL Slug": {
            "criteria": [
                ("Short Length", 3, "A short URL slug is easier to read and share, improving user experience and SEO."),
                ("Omission of Stop Words", 2, "Removing stop words from the URL makes it cleaner and more focused."),
                ("Aligns With Informational Architecture Of Domain", 4, "A URL that follows the site’s information architecture improves navigation and clarity."),
                ("Lowercase only", 2, "Using only lowercase letters in the URL helps avoid duplicate content issues."),
                ("Hyphens only", 2, "Hyphens should be used instead of underscores to separate words in the URL for better readability."),
                ("Non-parameterized (optional)", 1, "Avoiding parameters in URLs keeps them clean and easier to index."),
                ("ASCII characters only", 1, "Using ASCII characters in the URL ensures compatibility across different browsers and platforms."),
                ("Depth of 5 or less from the homepage", 2, "A shallow URL structure (five levels or less from the homepage) is easier for search engines to crawl.")
            ]
        },
        "Quality of Content": {
            "criteria": [
                ("Accuracy", 10, "Accurate content builds trust with users and search engines, which can improve rankings."),
                ("Originality", 9, "Original content is more likely to rank well because it provides unique value to users."),
                ("Tone Of Voice Matches Brand Standards", 8, "Consistency in tone of voice enhances brand recognition and user engagement."),
                ("Topic Completeness", 10, "Comprehensive content that covers a topic thoroughly is more likely to satisfy user intent and rank well."),
                ("Readability", 8, "Easy-to-read content improves user experience and retention, which can positively affect rankings."),
                ("Formatting (paragraph breaks, logical subheading structure)", 7, "Proper formatting helps users and search engines navigate the content more effectively."),
                ("Content Freshness / Regularly Updated", 9, "Regularly updating content keeps it relevant and improves its chances of ranking well."),
                ("Page Matches Expected User Intent", 10, "Ensuring the page matches user intent is critical for satisfying user needs and ranking well."),
                ("Other Pages Don't Cannibalize This One For Content", 8, "Avoiding content cannibalization ensures that this page has a better chance to rank for its target keywords.")
            ]
        }
    },
    "Off-Page": {
        "Page Authority vs Top 10": {
            "criteria": [
                ("Page Authority Is Greater Than Average Of Top 10 Results", 7, "A page with higher authority than its competitors is more likely to rank higher in search results.")
            ]
        },
        "Page Authority vs Top 3": {
            "criteria": [
                ("Page Authority Is Greater Than Average Of Top 3 Results", 9, "Having higher authority compared to the top 3 results can significantly improve ranking potential.")
            ]
        },
        "Backlinks from Relevant Domains": {
            "criteria": [
                ("Backlinks Are From Topically Relevant Domains", 7, "Links from relevant domains signal to search engines that your content is trustworthy and authoritative.")
            ]
        },
        "Backlink Placement": {
            "criteria": [
                ("Backlinks Are Placed Higher Up On Sourced Pages / Are Likely To Be Clicked", 3, "Backlinks that are prominently placed are more likely to be clicked and pass more authority.")
            ]
        },
        "Backlink Anchor Text": {
            "criteria": [
                ("Backlinks Contain Topically Relevant Anchor Text", 6, "Anchor text that includes relevant keywords helps search engines understand the context of the linked page.")
            ]
        },
        "Backlink Traffic": {
            "criteria": [
                ("Backlinks Are Placed On Pages That Actually Drive Visits", 7, "Backlinks from pages that drive traffic can increase the visibility and authority of your page.")
            ]
        }
    },
    "Technical": {
        "Canonical Tag": {
            "criteria": [
                ("Canonical Tag Contains Self-Reference", 6, "A canonical tag helps avoid duplicate content issues by telling search engines which version of a page is the preferred one.")
            ]
        },
        "Hreflang Tag": {
            "criteria": [
                ("Hreflang Tag (Optional) Is Correct, Targets The Right Locations, And References Other Translated Page Equivalents", 6, "This tag indicates to search engines which language you're using on a specific page and its regional targeting.")
            ]
        },
        "Indexability": {
            "criteria": [
                ("Page Is Indexable By Search Engines / Isn’t Blocked By Meta Tags Or Robots.txt", 10, "Ensuring that a page is indexable means it can be crawled and included in search results.")
            ]
        },
        "Sitemap Inclusion": {
            "criteria": [
                ("Page Is Included In Sitemap.xml file", 2, "Including a page in the sitemap.xml file helps search engines discover it more easily.")
            ]
        },
        "Page Orphan Status": {
            "criteria": [
                ("Page Isn’t Orphaned", 2, "Orphan pages, which are not linked to from other pages, can be harder for search engines to find and index.")
            ]
        },
        "Renderability": {
            "criteria": [
                ("Page Elements Are Renderable By Search Engines", 6, "Ensuring that search engines can properly render the page content is crucial for accurate indexing.")
            ]
        },
        "Web Core Vitals": {
            "criteria": [
                ("Page Passes Web Core Vitals Metrics / Exceeds Industry Average", 3, "These are a set of metrics related to speed, responsiveness, and visual stability, which affect user experience and ranking.")
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
    for i, (criterion, weight, help_text) in enumerate(criteria):
        with st.expander(f"{criterion} [Info]"):
            responses[criterion] = {
                "response": st.radio("", ["Yes", "No"], index=1, key=f"{factor}_{i}"),
                "weight": weight,
                "help": help_text
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

        recommendations = get_gpt4_recommendations(inputs)
        st.subheader("Recommendations")
        st.write(recommendations)

        export_to_word(inputs, scores, recommendations)
        st.success("Results exported to 'seo_audit_results.docx'")

if __name__ == "__main__":
    main()
