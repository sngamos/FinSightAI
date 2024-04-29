Problem Statement

--

Currently reports on quarterly/half-yearly/annual performance from Temasek Portfolio Companies/Temasek Investees are done and requested manually. How might we use GenAI to summarise these reports along with other documents such as call transcripts to produce key insights on trend movements for quarterly EBITDA,PATMI, Net debt trends?

Our Solution

--


Using GenAI, we created a multi-document RAG retriever that can:
1.	Accurately extract key financial metrics across multiple documents and tabulate them, together with the exact document and page number where this information was extracted from, hyperlinked with the metrics.
2.	Provide year on year financial narrative on the key metrics.
3.	Provide a multi-document QnA bot that can answer any further questions about the given documents accurate and form linkage between information between documents.

Credits: <br/>
Amos Sng <br/>
Michael Hoon <br/>
Ng Kin Meng <br/>
