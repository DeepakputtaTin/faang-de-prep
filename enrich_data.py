import json
import random

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    # Also save as data.js for static loading
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('const studyDataFromJS = ' + json.dumps(data) + ';')

def generate_content_for_topic(topic, action_item):
    # This acts as a simulated AI/Content generation engine.
    # We provide somewhat generic but highly contextual templates based on keywords in the topic.
    topic_lower = str(topic).lower()
    
    basics = f"Today we focus on {topic}. This is a critical concept in Data Engineering."
    key_concepts = [
        f"Understand the core mechanics of {topic}.",
        "Consider the performance implications when scaling.",
        "How does this integrate into the broader data pipeline?"
    ]
    hints = [
        "What is the input data structure?",
        "Can you break the transformation down into modular steps?",
        "What edge cases (like NULLs or skewed data) might break your logic?"
    ]
    hard_problem = "Design a system architecture that handles 1TB/day of data focusing on this concept."
    
    # Simple keyword matching for slightly better content
    if 'sql' in topic_lower or 'window' in topic_lower or 'join' in topic_lower:
        basics = f"SQL is the lingua franca of data. {topic} allows you to manipulate and analyze relational data efficiently. Pay special attention to execution order (FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY)."
        key_concepts = [
            "Difference between logical and physical execution plans.",
            "Handling NULLs and duplicate rows correctly.",
            "Index utilization and avoiding full table scans."
        ]
        hints = [
            "Write the query logic step-by-step using CTEs (WITH clauses).",
            "What happens if a join column contains NULLs?",
            "Can a window function replace a complex self-join here?"
        ]
        hard_problem = "Given a table of 1 billion user login events, write an optimized query to find the longest consecutive login streak for each user without using self-joins."
        
    elif 'python' in topic_lower or 'hash' in topic_lower or 'dictionary' in topic_lower or 'array' in topic_lower:
        basics = f"Python provides powerful built-in data structures. {topic} is essential for writing algorithms with optimal Time (Big-O) complexity."
        key_concepts = [
            "Time vs Space complexity tradeoffs.",
            "Under the hood memory allocation.",
            "When to use Generators vs Lists for large datasets."
        ]
        hints = [
            "Could a Hash Map (Dictionary) reduce your lookup time from O(N) to O(1)?",
            "Are you iterating over the data multiple times unnecessarily?",
            "Can you solve this in-place to save memory?"
        ]
        hard_problem = "Implement a custom Thread-Safe LRU Cache from scratch capable of handling high-concurrency requests."
        
    elif 'spark' in topic_lower or 'distributed' in topic_lower or 'partition' in topic_lower:
        basics = f"Distributed computing frameworks like Apache Spark divide data into partitions across a cluster. {topic} is key to preventing bottlenecks."
        key_concepts = [
            "The Shuffle: Why it's expensive and how to minimize it.",
            "Narrow vs Wide transformations.",
            "Handling Data Skew (Salting techniques)."
        ]
        hints = [
            "Is your data evenly distributed across partitions?",
            "Could a Broadcast Variable replace this Join?",
            "Check the Spark UI: Are tasks spilling to disk?"
        ]
        hard_problem = "You have a severely skewed dataset where 80% of transactions belong to one customer. Design a Spark job that joins this with a 50GB dimension table without OOM errors."
        
    elif 'model' in topic_lower or 'schema' in topic_lower or 'fact' in topic_lower:
        basics = f"Data Modeling ({topic}) is about structuring data for consumption. It balances storage cost, query performance, and ease of use for analysts."
        key_concepts = [
            "Star Schema vs Snowflake Schema tradeoffs.",
            "Handling Slowly Changing Dimensions (SCD Type 1, 2, 3).",
            "Choosing the right granularity for Fact tables."
        ]
        hints = [
            "What is the grain of this table? Does every row represent the same level of detail?",
            "Are these attributes changing rapidly or slowly?",
            "How will BI tools query this structure?"
        ]
        hard_problem = "Design the complete dimensional model (Facts and Dimensions) for an Uber-like ride-sharing application, accounting for rider/driver state changes and financial audits."
        
    elif 'orchestration' in topic_lower or 'airflow' in topic_lower:
        basics = f"Orchestrators like Airflow manage the dependencies and scheduling of pipelines. {topic} ensures pipelines run reliably and recover gracefully."
        key_concepts = [
            "Idempotency: Re-running a task should not duplicate data.",
            "Backfilling historical data.",
            "Sensors vs Operators."
        ]
        hints = [
            "What happens if this task fails halfway through?",
            "Are you hardcoding dates, or using logical execution dates (e.g. {{ ds }})?",
            "Can downstream tasks run even if some upstream tasks fail?"
        ]
        hard_problem = "Design a dynamic Airflow DAG architecture that automatically generates hundreds of pipelines based on a central metadata configuration database."

    return basics, key_concepts, hints, hard_problem


def enrich_data():
    data = load_data('clean_data.json')
    
    # Extract all distinct topics to use for the randomized warmup
    all_topics = []
    for day in data:
        topic = day.get('SpecificTopic') or day.get('ActionItem_Deliverable')
        if topic and topic not in all_topics:
            all_topics.append(topic)
            
    enriched_data = []
    past_topics = []
    
    for day in data:
        topic = day.get('SpecificTopic', 'General Data Engineering')
        action_item = day.get('ActionItem_Deliverable', '')
        theme = day.get('Theme', '')
        
        # 1. Warmup (Random previous topic)
        warmup = "No previous topics to review yet. Get started by focusing on today's core concepts!"
        if past_topics:
            warmup = f"Review Concept: **{random.choice(past_topics)}**. Can you explain it in 3 sentences?"
            
        if topic not in past_topics and topic != 'General Data Engineering':
            past_topics.append(topic)
            
        # Generate domain-specific dummy content
        search_string = f"{topic} {theme}"
        basics, key_concepts, hints, hard_problem = generate_content_for_topic(search_string, action_item)
        
        # 4. Practice Problem with Hints
        practice_problem = {
            "problem": f"**Daily Objective:** {action_item}",
            "hints": hints
        }
        
        # 6. LeetCode is already in the data as 'LeetCodeProblem'
        leetcode = day.get('LeetCodeProblem', 'No Specific LeetCode for today')
        if leetcode == "—" or type(leetcode) != str:
            leetcode = None
        
        # Update the day object
        day['Warmup'] = warmup
        day['Basics'] = basics
        day['KeyConcepts'] = key_concepts
        day['PracticeProblem'] = practice_problem
        if leetcode:
            # If they have a leetcode, make the Hard problem somewhat related to the action item
            day['HardProblem'] = hard_problem
        else:
            day['HardProblem'] = "Review day. Focus on internalizing the key concepts rather than solving a new hard problem."
            
        day['LeetCodeProblem'] = leetcode
        
        enriched_data.append(day)
        
    save_data(enriched_data, 'enriched_data.json')
    print(f"Successfully enriched {len(enriched_data)} days of study data and updated data.js.")

if __name__ == "__main__":
    enrich_data()
