from pathlib import Path
import json
import pandas as pd
import os

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS

# temporarilty add merger to sys path, call the function to merge jsons
# import sys
# sys.path.append('../py_scripts/merger')
# from merging import merge_jsons

# calling llm generation function
from utils.llm import get_completion

from utils.df_clean import cleanup_df, select_years

# set streamlit ui
st.set_page_config(page_title="GentlemAIn", page_icon="🚹", layout="wide", initial_sidebar_state="expanded")

vector_store = None
all_filenames_and_vectors = {}

FAISS_INDEX_DIR = "./data/faiss_index"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 512
filepath = "./data"

SCRIPT_FILEPATH = (os.path.dirname(os.path.abspath(__file__))).replace(" ", "%20")



QUICKSTATS_PROMPTS = {
                "Revenue" : """
        First, check if Total Revenue / Turnover is explicitly given in the context. If it is not, reply "None" as a single word.
        If it is, give me the Total Revenue / Turnover over the financial years available. DO NOT TAKE HALF or QUARTER years. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "Revenue (Millions)" : VALUE_AS_STRING
                    }
                ]
        }

        """,

                "EBITDA" : """
        First, check if EBITDA is explicitly given in the context. If it is not, reply "None" as a single word.
        
        If it is provided, give me the EBITDA over the financial years available. DO NOT TAKE HALF or QUARTER years. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "EBITDA (Millions)" : VALUE_AS_STRING
                    }
                ]
        }
        
        """,


        "EBITDA Margin" : """
        First, Check if EBITDA margin is explicitly given in the context. If it is not, reply "None" as a single word.
        If it is, give me the EBITDA MARGIN over the financial years available. DO NOT TAKE HALF or QUARTER years. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "EBITDA Margin (%)" : VALUE_AS_STRING
                        
                    }
                ]
        }
        """,

        "Passenger Load Factor" : """
        Analyze and extract only SIA passenger Load Factor from the context for all financial years.  DO NOT TAKE HALF or QUARTER years. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "Passenger Load Factor (%)" : VALUE_AS_STRING
                        
                    }
                ]
        }
        """,
        "Total Expenditure" : """
        Total Expenditure is definately explicitly given in the context for every year.
        Give me the Annual Total Expenditure for each FY. DO NOT TAKE figures from HALF yearly results. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "Total Expenditure (Millions)" : VALUE_AS_STRING
                        
                    }
                ]
        }
        """,
        "Basic EPS" : """
        Earnings/(loss) per share is definately explicitly given in the context for every year.
        Give me the Earnings/(loss) per share for each year. DO NOT TAKE figures from HALF yearly results. Output in JSON format like below. You can have multiple JSON entries:
        
        {
            "entries" : 
                [
                    {
                        "Company Name" : NAME, 
                        "Financial_Year" : FINANCIAL_YEAR,
                        "Basic EPS" : VALUE_AS_STRING
                        
                    }
                ]
        }"""
}


QNA_TEMPLATE = """Use the following pieces of context to answer the question at the end. DO NOT make up facts.

{context}

QUESTION: {question}

ANSWER:"""

# prompts for performance narrative
PERFORMANCE_PROMPT_2023 = """What are the key reasons driving financial performance in FY2022/23? Answer in point format in 5 reasons, explained succinctly, numbered by decreasing order of importance."""
PERFORMANCE_PROMPT_2022 = """What are the key reasons driving financial performance in FY2021/22? Answer in point format in 5 reasons, explained succinctly, numbered by decreasing order of importance."""
PERFORMANCE_PROMPT_2021 = """What are the key reasons driving financial performance in FY2020/21? Answer in point format in 5 reasons, explained succinctly, numbered by decreasing order of importance."""



#Custom class to store value with its metadata
class Value_With_Metadata():
    def __init__(self, value, metadata):
        self.value = value
        self.metadata = metadata
    
    def get_source_and_page_number(self):
        return self.metadata


    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
    
    def get_value(self):
        return self.value




@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@st.cache_data
def get_quick_stats(n_files):
    #n_files is to just make sure this runs again if we add a new file
    
    # complete_response = ""
    # combined_json_list = []
    metrics_df = None

    for key in QUICKSTATS_PROMPTS:
        all_metadata_lst = []
        try:
            #For each file, I gather the results, and then only collate those results to form a table
            for filename in all_filenames_and_vectors:
                vector_store = all_filenames_and_vectors[filename]["vector_store"]

                if vector_store:
                    context = ""
                    docs_and_scores = vector_store.similarity_search_with_score(
                        QUICKSTATS_PROMPTS[key], k=top_k
                    )
                    
                    metadata_lst = []

                    if docs_and_scores:
                        for doc, score in docs_and_scores:
                            context += f"\n{doc.page_content}"

                            #Remove the ./ at the start and replace the spaces with %20
                            cleaned_source = doc.metadata["source"][2:].replace(" ", "%20")

                            metadata_lst.append((cleaned_source, doc.metadata["page"]+1, doc.page_content)) #Store the filename and page number of each chunk chosen

                        updated_input = QNA_TEMPLATE.format(context=context, question=QUICKSTATS_PROMPTS[key])

                        messages = [
                            {"role": "system", "content": sys_message},
                            {"role": "user", "content": updated_input},
                        ]

                        response = get_completion(messages)

                        #convert into dictionary, then json file
                        reply = response.choices[0].message.content
                        # to prevent the case where the json format is bad
                        try:
                            data_dict = json.loads(reply)
                        except Exception as e:
                            print(e)
                            data_dict = {"entries": []} # as good as empty

                        all_filenames_and_vectors[filename]["metrics"] = data_dict

                        #Get the exact file and page that was used to get the results
                        if data_dict["entries"]:
                            for extracted_dict in data_dict["entries"]:
                                #Get the value at the 3rd key, which is the value of interest
                                #ChatGPT added the -ve to some numbers which was represented as () in the pdf
                                cleaned_value = list(extracted_dict.values())[2].replace("-", "")
                                
                                found_source = False

                                #Find for a document that has this value out of the 5 in the metadata lst
                                for source, page, page_content in metadata_lst:
                                    if cleaned_value in page_content:
                                        all_metadata_lst.append((source, page))
                                        found_source = True
                                        break
                                
                                if not found_source:
                                    all_metadata_lst.append(None)
                                    

            #Gather and combine all json files into a list
            temp_json_list = [all_filenames_and_vectors[filename]["metrics"]["entries"] for filename in all_filenames_and_vectors] #There are redundant inner lists
            temp_cleaned_json_list = []

            for json_list in temp_json_list:
                temp_cleaned_json_list.extend(json_list) #Remove redundant inner list

            #At this point, all_metadata_lst and temp_cleaned_json_list should have the same length
            metadata_index_counter = 0
            #Modify each value into the custom value wth metada object (that should print out the value)
            for dictionary in temp_cleaned_json_list:
                #Get the value key
                key = list(dictionary)[2]

                dictionary[key] = Value_With_Metadata(dictionary[key], all_metadata_lst[metadata_index_counter])
                metadata_index_counter += 1


            # Convert json into dataframe
            if metrics_df is None:
                metrics_df = pd.DataFrame.from_records(temp_cleaned_json_list)
                metrics_df["Financial_Year"] = pd.Series(["20"+year[-2:] for year in metrics_df["Financial_Year"]])
                metrics_df = cleanup_df(metrics_df)

            
            else:
                #To prevent duplicate rows
                temp_df = pd.DataFrame.from_records(temp_cleaned_json_list)
                temp_df["Financial_Year"] = pd.Series(["20"+year[-2:] for year in temp_df["Financial_Year"]])
                temp_df = cleanup_df(temp_df)

                metrics_df = metrics_df.merge(temp_df, on=['Company Name', 'Financial_Year'], how="left")
                metrics_df = select_years(metrics_df, "2021", "2023")
                
        except Exception as e:
            print(e)

    #Clean up further   
    metrics_df.drop_duplicates(subset=['Company Name', 'Financial_Year'], inplace=True)
    metrics_df.reset_index(inplace=True)
    metrics_df.drop(labels=["index"], axis=1, inplace=True)

    return metrics_df

embeddings = load_embeddings()

# load vector stores for each year of financial narrative
vector_store_2023 = FAISS.load_local(
    folder_path=FAISS_INDEX_DIR, 
    embeddings=embeddings,
    index_name="2. SIA - FY23.pdf"
    )
vector_store_2022 = FAISS.load_local(
    folder_path=FAISS_INDEX_DIR, 
    embeddings=embeddings,
    index_name="3. SIA - FY22.pdf"
    )
vector_store_2021 = FAISS.load_local(
    folder_path=FAISS_INDEX_DIR, 
    embeddings=embeddings,
    index_name="SIA - 2021.pdf"
    )

# calling llm generation for financial narrative
@st.cache_data
def financial_narrative_prompt(prompts, _vector_store):

    complete_response = ""
    context = ""

    docs_and_scores = _vector_store.similarity_search_with_score(
        prompts, k=top_k
    )

    if docs_and_scores:
        complete_response += f"{prompts}\n"
        for doc, score in docs_and_scores:
            context += f"\n{doc.page_content}"

        updated_input = QNA_TEMPLATE.format(context=context, question=prompts)

        messages = [
            {"role": "system", "content": sys_message},
            {"role": "user", "content": updated_input},
        ]

        response = get_completion(messages)
        complete_response += f"{response.choices[0].message.content}\n\n\n\n"

    return complete_response


file_raw_text = ""


st.title("🚹 GentlemAIn")

sys_message = "You are a financial analysis assistant. You should rely on the context provided only."

with st.sidebar:

    if uploaded_files := st.file_uploader(
        "Upload a file", type=["pdf"], accept_multiple_files=True
    ):
        
        #For each file, if it already exists, just load it
        for uploaded_file in uploaded_files:
            all_filenames_and_vectors[uploaded_file.name] = {}
            all_filenames_and_vectors[uploaded_file.name]["vector_store"] = None

            index_file = Path(f"{FAISS_INDEX_DIR}/{uploaded_file.name}.faiss")

            if index_file.exists():
                vector_store = FAISS.load_local(
                    folder_path=FAISS_INDEX_DIR,
                    embeddings=embeddings,
                    index_name=uploaded_file.name,
                )

                all_filenames_and_vectors[uploaded_file.name]["vector_store"] = vector_store

                st.success(f"{uploaded_file.name}.faiss in `{FAISS_INDEX_DIR}` loaded")

        top_k = 5

tab_key_metrics, tab_fin_narrative, tab_qna = st.tabs(["Key Metrics", "Financial Narrative", "Ask the Financial GENiAIses!"])

if uploaded_files is None:
    tab_key_metrics.write("Upload a pdf first!")
    tab_qna.write("Upload a pdf first!")
    tab_key_metrics.write("Upload a pdf first!")
    st.stop()

with tab_key_metrics:

    for filename in all_filenames_and_vectors:
        documents = PyMuPDFLoader(f"{filepath}/{filename}").load() #each document is a page

        # if vector does NOT exist, chunk it
        if not all_filenames_and_vectors[filename]["vector_store"]:
            #Get a full context of first 10 page of input pdf, which should likely have include the summary and make a full document summary
            full_context = ""
            for page in documents[:10]:
                full_context += f"\n\n{page.page_content}"

            #Get the full document summary
            prompt = f"""Based on the context below, provide a concise full document summary in not more one sentence. DO NOT INCLUDE NUMBERS. Your reply should be IMMEDIATELY the summary, do not start with "The summary of this document...". 

            {full_context}
            """
            messages = [
                {"role": "system", "content": sys_message},
                {"role": "user", "content": prompt},
            ]

            response = get_completion(messages)
            full_context_summary = response.choices[0].message.content

            with st.spinner("Chunking, generating and saving..."):
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
                )
                chunked_docs = text_splitter.split_documents(documents) #Tt is a list

                # add the summary into each chunk so that the full picture is always known
                for chunk in chunked_docs:
                    chunk.page_content += f"\n\nFullTextSummary: {full_context_summary}"

                vector_store = FAISS.from_documents(chunked_docs, embeddings)
                vector_store.save_local(
                    folder_path=FAISS_INDEX_DIR, index_name=filename
                )

                all_filenames_and_vectors[filename]["vector_store"] = vector_store

                st.success(
                    f"Generated {len(chunked_docs):,} chunks for {filename}"
                )

    # show financial metrics
    st.write("### Key Metrics")

    #Reply is the metrics_df
    metrics_df = get_quick_stats(len(all_filenames_and_vectors))

    for column in metrics_df:
        #if it is the financial year or company name ignore
        if not (column in ["Company Name", "Financial_Year"]):                     #Cases where the value could not be found in the source
            metrics_df[column] = metrics_df[column].apply(lambda value: value if ((not isinstance(value,Value_With_Metadata)) or value.metadata==None) else f"<a href='file:///{SCRIPT_FILEPATH}/{value.metadata[0]}#page={value.metadata[1]}'>{value}</a>")

    metrics_html = metrics_df.to_html(escape=False, render_links=True)

    st.markdown(metrics_html, unsafe_allow_html=True)


with tab_fin_narrative:
    #Do pre determined query to get basic financial stats
    if not vector_store:
        st.write("Process uploaded pdf file first under the `File Content` tab!")
    else:
        # st.write("⌨ █▬▬◟(`ﮧ´ ◟ ) Rage Quit!!! (╯°□°）╯︵ ┻━┻")

        st.write("### 2023")
        reply = financial_narrative_prompt(PERFORMANCE_PROMPT_2023, vector_store_2023)
        st.write(reply.replace("$", r"\$"))

        st.divider()

        st.write("### 2022")
        reply = financial_narrative_prompt(PERFORMANCE_PROMPT_2022, vector_store_2022)
        st.write(reply.replace("$", r"\$"))

        st.divider()

        st.write("### 2021")
        reply = financial_narrative_prompt(PERFORMANCE_PROMPT_2021, vector_store_2021)
        st.write(reply.replace("$", r"\$"))

        st.divider()


with tab_qna:
    if not vector_store:
        st.write("Process uploaded pdf file first under the `File Content` tab!")
    else:
        st.write("### Question")
        if user_input := st.text_area(""):
            st.divider()
            context = ""
            all_docs_and_scores = [] # will hold ALL docs and scores across all the vector stores

            # iteratively find for the top k matches in documents
            for filename in all_filenames_and_vectors:
                vector_store = all_filenames_and_vectors[filename]["vector_store"]

                docs_and_scores = vector_store.similarity_search_with_score(
                    user_input, k=top_k
                )

                #Add all to the main list
                all_docs_and_scores.extend([(score, doc) for doc, score in docs_and_scores])
            
            #Lower score is better, think as "distance" between the document and the input
            #So sort in ascending order, will sort by score first by tuple comparison
            all_docs_and_scores.sort()

            #Get the top k elements
            top_k_docs_and_scores = all_docs_and_scores[:top_k]

            st.write("### Answer")
            st.divider()
            if top_k_docs_and_scores:
                for score, doc in all_docs_and_scores:
                    context += f"\n{doc.page_content}"

                updated_input = QNA_TEMPLATE.format(context=context, question=user_input)
                messages = [
                    {"role": "system", "content": sys_message},
                    {"role": "user", "content": updated_input},
                ]

                response = get_completion(messages)
                reply = response.choices[0].message.content
                st.write(reply.replace("$", r"\$"))  # fix dollar sign issue

                st.write("### Document Chunks Retrieved")
                st.divider()
                for score, doc in top_k_docs_and_scores:
                    with st.expander(
                        label=f'Source: {doc.metadata["source"]}, Page: {doc.metadata["page"]+1}, Score: {score:.3f}',
                        expanded=False,
                    ):
                        st.text(doc.page_content)