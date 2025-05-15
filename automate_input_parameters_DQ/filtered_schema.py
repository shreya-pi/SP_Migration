from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



class FilterSchema:

    def filter_schema(self, input_parameters, schema_text):
    
        schema_chunks = [chunk.strip() for chunk in schema_text.split("[SEP]") if chunk.strip()]
        model = SentenceTransformer('all-MiniLM-L6-v2') 
        # Encode schema chunks
        schema_embeddings = model.encode(schema_chunks)
        
        # query_embedding = model.encode([input_parameters])
        query_embedding = model.encode([" ".join(input_parameters)])
        
        # Compute similarity between input and each schema chunk
        similarities = cosine_similarity(query_embedding, schema_embeddings)[0]
        
        # Sort indices of top relevant schemas
        top_n = 6  # pick how many most relevant you want
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        # After getting top N by embedding similarity:
        filtered_candidates = [schema_chunks[i] for i in top_indices]
        
        # Now re-rank based on parameter coverage
        ranked = sorted(filtered_candidates, key=lambda x: self.score_schema(x, input_parameters), reverse=True)
        
        # Pick the top schema with most matching parameters
        filtered_schema = ranked[0]
        # filtered_schema = [ranked[i] for i in top_indices]
        print("Filtered Schema:")
        print(filtered_schema)

        return filtered_schema
    


    def score_schema(self, schema_str, input_params):
        score = 0
        for param in input_params:
            if param in schema_str:
                score += 1
        return score
