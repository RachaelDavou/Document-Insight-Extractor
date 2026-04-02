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



