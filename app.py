import streamlit as st
import pandas as pd
import requests

# --- Function to fetch results ---
def fetch_serp_results(api_key, query, country_code):
    params = {
        "engine": "google",
        "q": query,
        "location": country_code,
        "google_domain": "google.com",
        "gl": country_code,
        "hl": "en",
        "num": 10,
        "api_key": api_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    if "organic_results" in data:
        urls = [result["link"] for result in data["organic_results"]]
        return urls
    else:
        return []

# --- Function to compare results ---
def calculate_similarity(urls1, urls2):
    set1 = set(urls1)
    set2 = set(urls2)
    matches = set1.intersection(set2)
    similarity_percentage = (len(matches) / 10) * 100 if len(urls1) > 0 and len(urls2) > 0 else 0
    return similarity_percentage, matches

# --- Function to create a DataFrame ---
def create_comparison_df(urls1, urls2, matches):
    data = []
    for url in urls1:
        data.append({
            "Keyword 1 URL": url,
            "Match with Keyword 2?": "✅" if url in matches else "❌"
        })
    for url in urls2:
        if url not in urls1:
            data.append({
                "Keyword 1 URL": "",
                "Keyword 2 URL": url,
                "Match with Keyword 1?": "✅" if url in matches else "❌"
            })
    df = pd.DataFrame(data)
    return df

# --- Streamlit UI ---
st.set_page_config(page_title="SERP Similarity Checker", page_icon="🔍", layout="centered")

st.title("🔍 SERP Similarity Checker")

st.write("Compare the top 10 Google search results for two keywords and download the results!")

st.markdown("---")

api_key = st.text_input("🔑 Enter your SerpAPI Key", type="password")
keyword1 = st.text_input("📝 Enter Keyword 1")
keyword2 = st.text_input("📝 Enter Keyword 2")
country_code = st.text_input("🌎 Enter Country Code (e.g., US, IN)").upper()

if st.button("🚀 Check Similarity"):
    if not api_key or not keyword1 or not keyword2 or not country_code:
        st.warning("Please fill all fields before proceeding!")
    else:
        with st.spinner("Fetching SERP results..."):
            urls1 = fetch_serp_results(api_key, keyword1, country_code)
            urls2 = fetch_serp_results(api_key, keyword2, country_code)

        if urls1 and urls2:
            similarity, matches = calculate_similarity(urls1, urls2)

            st.success(f"🔗 Similarity Score: **{similarity:.2f}%**")

            st.markdown("---")
            st.subheader("🔎 Matching URLs:")

            if matches:
                for url in matches:
                    st.write(f"✅ {url}")
            else:
                st.write("❌ No matching URLs found.")

            st.markdown("---")
            st.subheader("📋 Full Comparison Table")

            # Create comparison DataFrame
            data = []
            for i in range(10):
                url1 = urls1[i] if i < len(urls1) else ""
                url2 = urls2[i] if i < len(urls2) else ""
                match = "✅" if url1 in matches and url1 != "" else ("✅" if url2 in matches and url2 != "" else "❌")
                data.append({
                    "Rank": i+1,
                    "Keyword 1 URL": url1,
                    "Keyword 2 URL": url2,
                    "Match?": match
                })
            df = pd.DataFrame(data)

            st.dataframe(df, use_container_width=True)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name='serp_similarity_results.csv',
                mime='text/csv',
            )
        else:
            st.error("⚠️ Failed to fetch search results. Please check your API key, keywords, or country code.")
