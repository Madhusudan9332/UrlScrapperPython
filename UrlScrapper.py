import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


file_path = "data.xlsx"
df = pd.read_excel(file_path)

folder_name = "pages"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Initialize a new column for scraped content
df['Scraped_Content'] = None
unfatched_urls = []

def scrapData(index,url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract specific data (e.g., the title of the page)
            title = soup.title.string if soup.title else "No title"
            
            # Extract headings
            headings = [h.get_text(strip=True) for h in soup.find_all('h1')]
            
            # Extract all paragraphs
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            
            # Combine extracted data into a structured string
            scraped_data = f"Title: {title}; Headings: {', '.join(headings)}; Paragraphs: {' '.join(paragraphs)}"
            
            # Generate HTML content with all data
            headings_html = "".join(f"<h1>{h}</h1>" for h in headings)
            paragraphs_html = "".join(f"<p>{p}</p>" for p in paragraphs)
            html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{title}</title>
                </head>
                <body>
                    <h1>{title}</h1>
                    <h2>Headings:</h2>
                    {headings_html}
                    <h2>Paragraphs:</h2>
                    {paragraphs_html}
                </body>
                </html>
                """
            file_name = f"{folder_name}/page_{index}.html"
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(html_content)
                
            print(f"HTML content saved to {file_name}")
            # Store the scraped data in the DataFrame
            df.at[index, 'Scraped_Content'] = scraped_data
        else:
            df.at[index, 'Scraped_Content'] = f"Failed to fetch: {response.status_code}"
    except Exception as e:
        df.at[index, 'Scraped_Content'] = f"Error: {e}"
        return False
    return True


# Scrape content for each URL
for index, row in df.iterrows():
    url = row['url']
    max_attempts = 3
    success = False
    # while(scrapData(index,url) == False and attempt < max_attempts):
    for attempt in range(max_attempts):
        if(scrapData(index,url) == True):
            success = True
            break
        print(f"{attempt + 1} attempt done Data not fetched")
    if(success == False):
        print(f"check the Url : {url} ,3 attempts failed")
        unfatched_urls.append(url)
    print("Data fetched")
        
unfatched_urls_file = f"{folder_name}/unfatched_urls.txt"
with open(unfatched_urls_file, "w", encoding="utf-8") as file:
    file.write(f"These are the unfatched urls : {unfatched_urls}")


# Display the updated DataFrame 
print(df)

# Save the updated DataFrame to a new Excel file
df.to_excel("new_scraped_data.xlsx", index=False)
