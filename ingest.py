import os, requests, shutil, time
from bs4 import BeautifulSoup
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Official NVDA 2026.1 Manual
URL = "https://download.nvaccess.org/releases/2026.1beta7/documentation/userGuide.html"

def build_the_brain():
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")

    print("Step 1: Downloading NVDA 2026.1 Manual...")
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    documents = []
    
    print("Step 2: Processing Hierarchy and Shortcuts...")
    # We track the current section to give context to every chunk
    current_section = "General NVDA"
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'table']):
        if element.name in ['h1', 'h2', 'h3']:
            current_section = element.get_text().strip()
        
        elif element.name == 'table':
            rows = []
            for tr in element.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if len(cells) >= 2:
                    rows.append(f"Command: {cells[0]} | Action: {cells[1]}")
            if rows:
                content = f"Section: {current_section}\n" + "\n".join(rows)
                documents.append(Document(page_content=content, metadata={"source": "nvda_manual", "type": "shortcuts"}))
        
        elif element.name in ['p', 'li']:
            text = element.get_text().strip()
            if len(text) > 80:
                content = f"Context: {current_section}\nInstruction: {text}"
                documents.append(Document(page_content=content, metadata={"source": "nvda_manual", "type": "instruction"}))

    print(f"Step 4: Saving {len(documents)} chunks (Fast Mode)...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # PAID TIER: Process in large batches with minimal sleep
    batch_size = 100 
    vectorstore = None
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        print(f"  Writing batch {i//batch_size + 1}...")
        if vectorstore is None:
            vectorstore = Chroma.from_documents(batch, embeddings, persist_directory="./chroma_db")
        else:
            vectorstore.add_documents(batch)
        time.sleep(1) # Tiny safety pause

    print("Success! AccessCompanion library is built.")

if __name__ == "__main__":
    build_the_brain()