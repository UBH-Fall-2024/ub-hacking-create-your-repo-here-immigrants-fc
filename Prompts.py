from langchain_chroma import Chroma
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
import embeddings
import argparse
import json
from json_stuff import clean_and_validate_json 
import re
import traceback  
import time 

CHROME_PATH = "./chroma"


model = Ollama(model = "llama3.2")

PROMPT_TEM_SCHEDULE = """
You are a personal Assistant for the user. Your task is to create a schedule based ONLY on the tasks specifically mentioned by the user.

Context:
{context}

User Question: {question}

Instructions for Schedule Creation:
1. ONLY include tasks that the user explicitly mentions
2. NEVER create or add tasks that weren't specified by the user
3. Break tasks into appropriate time chunks if they're large tasks
4. Add 5-minute breaks between major tasks
5. For each task identified from the user's message:
   - Allocate realistic time based on the task complexity
   - Give specific, task-focused descriptions
   - Keep original task context and purpose

Format each task as:
TaskName (X minutes): Specific description from user's context

IMPORTANT:
- Do not invent or add tasks
- Only schedule what the user explicitly requests
- Keep descriptions focused on the user's actual tasks
- Add breaks only between major tasks
- Be specific about which part of the task is being done

Example (only if these were actually mentioned by user):
Math Homework (25 minutes): Complete algebra equations 1-10
Break (5 minutes): Short rest
Science Project (30 minutes): Work on lab report introduction

Your response should contain ONLY tasks mentioned by the user, with appropriate timing.
"""

FORMATTED_SCHEDULE = '''
Convert ONLY the tasks mentioned by the user into this exact JSON format. 
DO NOT add any tasks that weren't in the user's request.

THE SCHEDULE: {schedule}

Required JSON Format:
{
    "Action": "New_Timer",
    "Timer_Items": {
        "Item1": {
            "Time Needed": "X minutes",
            "Description": "exact task from user"
        }
    }
}

STRICT RULES:
1. Only include tasks specifically requested by the user
2. Never add extra or assumed tasks
3. Include short breaks only between actual tasks
4. Keep descriptions directly related to user's tasks
5. Use exact task names from user's request
6. Time format must be "X minutes" where X is a number
7. Break down large tasks if needed, but maintain user's intent

Example (only if these were the actual user tasks):
{
    "Action": "New_Timer",
    "Timer_Items": {
        "Item1": {
            "Time Needed": "30 minutes",
            "Description": "Complete math homework chapters 1-2"
        },
        "Item2": {
            "Time Needed": "5 minutes",
            "Description": "Break"
        },
        "Item3": {
            "Time Needed": "45 minutes",
            "Description": "Write English essay introduction"
        }
    }
}

REMEMBER: Include ONLY tasks from the user's request. Don't add any extras.
'''

'''
def extract_tasks_from_text(text):
    """Extract tasks and times from text description"""
    tasks = []
    lines = text.split('\n')
    for line in lines:
        if '(' in line and ')' in line and 'minutes' in line.lower():
            task_match = re.match(r'(.*?)\s*\((\d+)\s*minutes\):\s*(.*)', line)
            if task_match:
                task_name = task_match.group(1).strip()
                time = task_match.group(2)
                description = task_match.group(3).strip()
                if task_name and time and description:
                    tasks.append({
                        "name": task_name,
                        "time": time,
                        "description": description
                    })
    return tasks

def make_query(text):
    """Process user text and return formatted schedule"""
    embedding_function = embeddings.get_embeddings()
    model = Ollama(model="llama3.2", temperature=0.3)
    datab = Chroma(persist_directory=CHROME_PATH, embedding_function=embedding_function)

    try:
        # Get similar documents
        results = datab.similarity_search_with_score(text, k=7)  
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        # First prompt to get the schedule
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEM_SCHEDULE)
        prompt_initial = prompt_template.format(context=context, question=text)
        response_wild = model.invoke(prompt_initial)
        formatted_wild = str(response_wild).strip()
        
        print("\nInitial schedule:")
        print(formatted_wild)
        
        # Extract tasks from the initial response
        tasks = extract_tasks_from_text(formatted_wild)
        
        # Create the JSON structure directly
        schedule_data = {
            "Action": "New_Timer",
            "Timer_Items": {}
        }
        
        if tasks:
            for i, task in enumerate(tasks, 1):
                schedule_data["Timer_Items"][f"Item{i}"] = {
                    "Time Needed": f"{task['time']} minutes",
                    "Description": f"{task['name']}: {task['description']}"
                }
                
                # Add breaks between major tasks
                if i < len(tasks):
                    break_item = {
                        "Time Needed": "5 minutes",
                        "Description": "Short break to maintain focus"
                    }
                    schedule_data["Timer_Items"][f"Item{i}_break"] = break_item
        else:
            # Handle case where no tasks were extracted
            task_parts = text.split(" and ")
            total_time = 240  # 4 hours in minutes
            time_per_task = total_time // len(task_parts)
            
            for i, task in enumerate(task_parts, 1):
                schedule_data["Timer_Items"][f"Item{i}"] = {
                    "Time Needed": f"{time_per_task} minutes",
                    "Description": task.strip()
                }
                
                # Add break between tasks
                if i < len(task_parts):
                    schedule_data["Timer_Items"][f"Item{i}_break"] = {
                        "Time Needed": "5 minutes",
                        "Description": "Short break to maintain focus"
                    }
        
        print("\nFormatted schedule:")
        print(json.dumps(schedule_data, indent=2))
        
        return json.dumps(schedule_data)
            
    except Exception as e:
        print(f"Error in make_query: {str(e)}")
        traceback.print_exc()
        
        # Create a minimal schedule from the user's input
        task_parts = text.split(" and ")
        total_time = 240  # 4 hours in minutes
        time_per_task = total_time // len(task_parts)
        
        schedule_data = {
            "Action": "New_Timer",
            "Timer_Items": {}
        }
        
        for i, task in enumerate(task_parts, 1):
            schedule_data["Timer_Items"][f"Item{i}"] = {
                "Time Needed": f"{time_per_task} minutes",
                "Description": task.strip()
            }
            if i < len(task_parts):
                schedule_data["Timer_Items"][f"Item{i}_break"] = {
                    "Time Needed": "5 minutes",
                    "Description": "Short break to maintain focus"
                }
        
        return json.dumps(schedule_data)
'''

def extract_tasks_from_text(text):
    """Extract tasks and times from text description, ignoring redundant breaks"""
    tasks = []
    lines = text.split('\n')
    last_was_break = False
    
    for line in lines:
        if '(' in line and ')' in line and 'minutes' in line.lower():
            task_match = re.match(r'(.*?)\s*\((\d+)\s*minutes\):\s*(.*)', line)
            if task_match:
                task_name = task_match.group(1).strip()
                time = task_match.group(2)
                description = task_match.group(3).strip()
                
                
                is_break = 'break' in task_name.lower()
                if is_break and last_was_break:
                    continue
                    
                if task_name and time and description:
                    tasks.append({
                        "name": task_name,
                        "time": time,
                        "description": description,
                        "is_break": is_break
                    })
                    last_was_break = is_break
    return tasks

def make_query(text):
    """Process user text and return formatted schedule"""
    embedding_function = embeddings.get_embeddings()
    model = Ollama(model="llama3.2", temperature=0.3)
    datab = Chroma(persist_directory=CHROME_PATH, embedding_function=embedding_function)

    try:
        
        results = datab.similarity_search_with_score(text, k=7)  
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
       
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEM_SCHEDULE)
        prompt_initial = prompt_template.format(context=context, question=text)
        response_wild = model.invoke(prompt_initial)
        formatted_wild = str(response_wild).strip()
        
        print("\nInitial schedule:")
        print(formatted_wild)
        
        
        tasks = extract_tasks_from_text(formatted_wild)

        schedule_data = {
            "Action": "New_Timer",
            "Timer_Items": {}
        }
        
        if tasks:
            item_count = 1
            last_was_break = False
            
            for task in tasks:
                
                if task['is_break'] and last_was_break:
                    continue
                    
                schedule_data["Timer_Items"][f"Item{item_count}"] = {
                    "Time Needed": f"{task['time']} minutes",
                    "Description": f"{task['name']}: {task['description']}"
                }
                

                item_count += 1
                last_was_break = task['is_break']
                
                
                if not task['is_break'] and not any(t['is_break'] for t in tasks[tasks.index(task)+1:tasks.index(task)+2]):
                    schedule_data["Timer_Items"][f"Item{item_count}_break"] = {
                        "Time Needed": "5 minutes",
                        "Description": "Short break to maintain focus"
                    }
                    item_count += 1
                    last_was_break = True
        else:

            task_parts = text.split(" and ")
            total_time = 240 
            time_per_task = total_time // len(task_parts)
            
            for i, task in enumerate(task_parts, 1):
                schedule_data["Timer_Items"][f"Item{i}"] = {
                    "Time Needed": f"{time_per_task} minutes",
                    "Description": task.strip()
                }
                

                if i < len(task_parts):
                    schedule_data["Timer_Items"][f"Item{i}_break"] = {
                        "Time Needed": "5 minutes",
                        "Description": "Short break to maintain focus"
                    }
        
        print("\nFormatted schedule:")
        print(json.dumps(schedule_data, indent=2))
        
        return json.dumps(schedule_data)
            
    except Exception as e:
        print(f"Error in make_query: {str(e)}")
        traceback.print_exc()

        task_parts = text.split(" and ")
        total_time = 240  
        time_per_task = total_time // len(task_parts)
        
        schedule_data = {
            "Action": "New_Timer",
            "Timer_Items": {}
        }
        
        for i, task in enumerate(task_parts, 1):
            schedule_data["Timer_Items"][f"Item{i}"] = {
                "Time Needed": f"{time_per_task} minutes",
                "Description": task.strip()
            }
            if i < len(task_parts):
                schedule_data["Timer_Items"][f"Item{i}_break"] = {
                    "Time Needed": "5 minutes",
                    "Description": "Short break to maintain focus"
                }
        
        return json.dumps(schedule_data)


def validate_schedule_format(schedule_data):
    """Validate the schedule format and content"""
    if not isinstance(schedule_data, dict):
        return False
        
    if 'Action' not in schedule_data or schedule_data['Action'] != 'New_Timer':
        return False
        
    if 'Timer_Items' not in schedule_data or not isinstance(schedule_data['Timer_Items'], dict):
        return False
        
    for item_name, item_data in schedule_data['Timer_Items'].items():
        if not isinstance(item_data, dict):
            return False
            
        if 'Time Needed' not in item_data or 'Description' not in item_data:
            return False
            

        time_str = item_data['Time Needed']
        if not re.match(r'^\d+\s+minutes$', time_str):
            return False

        minutes = int(re.search(r'\d+', time_str).group())
        if minutes <= 0:
            return False

        if not item_data['Description'].strip():
            return False
            
    return True
