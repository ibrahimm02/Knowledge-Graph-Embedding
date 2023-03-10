To open the Project as a folder:
* Open Knowledge-Graph-Embedding as a project in the IDE


To run the project the entry point is:
* Main.py. Please run this to generate all the necessary data for task up until Alignment Querying (Subtask OA.3)


To run the Ontology Embeddings (Task Vector) - Subtask Vector.1 
* Navigate to the embeddings folder and open the terminal.
* pip install setuptools
* owl2vec_star standalone --config_file default.cfg
* The output files will be generated in cache/
* annotations.txt, axioms.txt, entities.txt, outputontology.embeddings, outputontology.embeddings.txt, projection.ttl 




To run Subtask Vector.2 & Subtask Vector.3:
* Navigate to embeddings folder
* Open New-Embedding.ipynb using Jupyter