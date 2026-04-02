# Document Insight Extractor

An AI agent that reads PDF and text documents and extracts structured insights using LangChain tools. Includes the ability to fetch sample documents directly from GitHub.


## Requirements

Install the dependencies:

```
pip install streamlit langchain langchain-openai langchain-community pypdf pydantic requests
```
You will also need an OpenAI API key. Get one at https://platform.openai.com/api-keys


## How to Run

1. Open `insight_extractor.py` and replace the placeholder with your OpenAI API key:

```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

2. Run the app from the command line:

```
streamlit run insight_extractor.py
```

The app will open a local host in your browser.


## Sample Documents

The app can fetch sample documents directly from GitHub. Two samples are included:

- **Business Memo** - State of the Union text from LangChain repo
- **Paul Graham Essay** - Startup ideas essay from langchain-tutorials repo

Select a sample from the dropdown and click "Load Sample" to fetch it.


## How It Works

The application integrates three tools to process documents and extract structured data.

1. **Document Loader Tool** - Uses LangChain's PyPDFLoader or TextLoader to read uploaded files and extract text content along with metadata
2. **GitHub Fetcher Tool** - Uses the requests library to fetch raw text files from GitHub URLs
3. **Insight Extractor Tool** - Sends the content to GPT-4o-mini with a Pydantic schema that defines exactly what fields to extract
4. **Structured Output** - The LLM returns data that conforms to the Pydantic model, which validates the response and converts it to a Python object


