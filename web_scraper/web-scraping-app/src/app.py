import streamlit as st
import pandas as pd
from scraper.scraper import Scraper
from visualization.charts import create_chart

def main():
    st.title("Web Scraping App")
    
    # User Input Layer
    url = st.text_input("Enter URL:")
    tags = st.text_input("Enter CSS/XPath tags (comma-separated):")
    frequency = st.number_input("Scraping Frequency (in minutes):", min_value=1, value=5)
    data_type = st.selectbox("Select Data Type:", ["Text", "Images", "Tables"]).lower()  # Convert to lowercase
    
    if st.button("Scrape"):
        if url:
            tags_list = [tag.strip() for tag in tags.split(",")]
            scraper = Scraper()
            data = scraper.scrape_data(url, tags_list, data_type)
            
            if data is not None:
                st.success("Data scraped successfully!")
                st.write(data)
                
                # Visualization
                chart = create_chart(data)
                st.altair_chart(chart, use_container_width=True)
                
                # Export Capability
                if st.button("Download as CSV"):
                    csv = data.to_csv(index=False)
                    st.download_button("Download CSV", csv, "scraped_data.csv", "text/csv")
                
                if st.button("Download as JSON"):
                    json_data = data.to_json()
                    st.download_button("Download JSON", json_data, "scraped_data.json", "application/json")
            else:
                st.error("Failed to scrape data. Please check the URL and tags.")
        else:
            st.warning("Please enter a valid URL.")

if __name__ == "__main__":
    main()