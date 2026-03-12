	
Planned Improvements
	•	Improve regex to support special characters in algorithm names.
	•	Expand topic taxonomy and mappings.
	•	Add additional normalization rules for topic names.
    
	(after llm call, mapping will be executed on response of llm if model make a mistakes it will detect and fixed if no mistakes found llm response will be send)
	• alias resolution layer olarak eklenmeli


Known Limitations
    •	Regex does not detect some algorithms containing special characters (e.g., A*).
	•	Some topics are missed if they are not present in the topic mapping (e.g., Stack, 	Queue, Linked List).
	•	LLM may sometimes classify a general topic as a specific topic (e.g., Graph Algorithms).
	•	Taxonomy coverage is still limited and needs to be expanded.