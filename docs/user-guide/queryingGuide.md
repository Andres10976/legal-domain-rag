# Querying Documents

This guide explains how to effectively query your legal documents using the Legal Domain RAG System.

## Query Interface

The query interface is available at the `/query` route in the web application. This interface includes:

- A query input box
- A response display area
- Citation sources with expandable details
- Query history (optional)

## Formulating Effective Queries

The system uses natural language processing to understand your queries, so you can ask questions in plain English. However, there are some tips to get the best results:

### Be Specific

The more specific your query, the more precise the response will be. For example:

- Less effective: "What does the contract say about termination?"
- More effective: "What are the conditions for early termination in the Wilson Services Agreement?"

### Include Key Terms

Using terminology that appears in the documents helps the system find relevant information:

- Less effective: "What are my options if they don't deliver?"
- More effective: "What remedies are available for breach of delivery obligations under the supply agreement?"

### Ask One Question at a Time

For complex inquiries, break them down into separate questions:

- Less effective: "What are the payment terms, delivery schedule, and warranty provisions?"
- More effective: First ask about payment terms, then delivery schedule, then warranty provisions

## Understanding Responses

The system provides responses based solely on the content of your documents, using a retrieval-augmented generation approach:

1. Your query is converted to a vector embedding
2. The system finds the most relevant document chunks
3. These chunks are used as context to generate a response
4. The response includes citations to the source material

### Interpreting Citations

Each response includes citations to the source documents. Citations appear as numbers in square brackets, like [1] or [2].

You can click on these citations to expand and view the original text from the document. This allows you to verify the information and see the broader context.

### Confidence Score

Each response includes a confidence score, indicating how confident the system is in the accuracy of the response:

- **High Confidence (Green)**: The response is well-supported by the documents
- **Medium Confidence (Yellow)**: The response is partially supported but may have some uncertainties
- **Low Confidence (Red)**: The response has limited support in the documents

For low-confidence responses, you should carefully review the source citations and consider reformulating your query.

## Query History

The system may store your recent queries in the current session. You can click on a previous query to rerun it, which is useful for:

- Iteratively refining your questions
- Revisiting important information
- Comparing responses to different but related questions

## Example Queries

Here are some examples of effective queries for common legal document types:

### Contracts

- "What are the payment terms in the Johnson Manufacturing Agreement?"
- "Under what circumstances can the Smith Consulting Agreement be terminated?"
- "What are the confidentiality obligations for both parties in the NDA dated January 2023?"

### Case Law

- "What was the court's reasoning for denying the motion in Jones v. Smith?"
- "What precedent did the court cite regarding liability in the Baker case?"
- "What standard of review did the appellate court apply in the Wilson decision?"

### Statutes and Regulations

- "What are the requirements for filing a Form 8-K under Section 13 of the Securities Exchange Act?"
- "What penalties apply for violations of Regulation S-P under the SEC rules?"
- "What exemptions are available under California Consumer Privacy Act for small businesses?"

## Best Practices

- **Start broad, then narrow**: Begin with a general question, then ask more specific follow-up questions
- **Verify sources**: Always check the cited sources for context and accuracy
- **Reformulate**: If you don't get a satisfactory answer, try rephrasing your question
- **Use legal terminology**: Using precise legal terms will help the system find relevant information
