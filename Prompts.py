from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate

model = Ollama(model = "llama3.2")

PROMPT_TEM_SCHEDULE = """
You are a personal Assistant for the user. You will be provided a list of tasks that need completing and a time frame, and your job is to
create a schedule for the user that meets the time frame and completes all tasks in the most efficient way possible. You can ask for clarification, but I want you to use any previous knowledge
you have on deep learning and the flow state, including concepts like the pomodoro technique and build the most efficient work flow you can.
Context:
{context}

User Question: {question}

Instructions
1. Carefully analyze the timeframe, the provided context, and the user's tasks.
2. Make sure to use the provided context for planning ONLY. Do not let it affect the tasks at all. 
3. When creating a schedule, feel free to break up the tasks however you deem best, based on the provided context and ther perceived difficulty of the tasks, but ALWAYS make sure to adhere to the time constraint set by the user.
Do not provide specific time ranges for each task, but just show how long each will last.
4. Make sure to include breaks in the schedule as needed. Base the break timing and length on the various techniques in the context and on your own personal knowledge. 
5. If there is no provided context, please state "There is no provided context " followed by a response to the user that is made entirely on your own knowledge. Only do this if there is no context provided.
6. If you need further clarification on something, please ask the user for more information.
7. The tasks must be broken up in the most efficient way possible, Allowing the user to leverage deep work and the flow state to finish the tasks at the best of their ability.
8. When providing the schedule, include the time to work on the task, the task itself. Do the same for breaks.
9. Make sure to list some actvities the user can do during breaks that will allow them to rest, but also not lose focus.
10. Understand that some tasks may not be finished within the required time, so you do not necessarily need to expect bigger tasks to be finished within the given time limit.
11. When providing an answer, write NOTHING other than the tasks, the time for each, and descriptions and tips for each.
"""
context_texts = ""
quested_text = "I have an assignment to finish and I need to study for two tests. My assignment is a programming project, and I have to study for mty discrete math quiz and calc 2 midterm. I plan on spending 6 hours working on them today, how do I spread them out?"
prompted = ChatPromptTemplate.from_template(PROMPT_TEM_SCHEDULE)
prompt = prompted.format(context = context_texts, question = quested_text)
response = model.invoke(prompt)
forms = f"{response}"
print(forms) 

FORMATTED_SCHEDULE = '''
Today you will parse some information for me. I will provide you with text which contains a schedule full of different tasks, their duration, and 
some additional information about it. You are to format the information based on the specifications provided to you in the instructions. 
THE SCHEDULE: {schedule}
Instructions:
1. I need you to return your response to me in the JSON format, just as is described below. Make sure you follow the format exacly and removfe any newline characters from the sentences as they appear.:
an example is {{"Action":"what to do", "Timer_Items":{{"Item":{{"Time Needed":"Description"}}, "Item2":{{"Time Needed":"Description"}}, "Item3":{{"Time Needed":"Description"}}}}, "User":"Response"}}
Explanation and rules:
"Action" describes what the code will be executing, you will fill the "what to do" field with ONLY one of the following: "NONE", "New_Timer", "Start_Timer", 
or "Pause_Timer" depending on the user needs. There will only be ONE of these actions per user request. If the user tells you what you about the tasks to be completed, you will return a "New_Timer" object.if they tell you to start the time, you return "Start_Timer".
If they tell you to pause it, you return "Pause_Timer".
2. Every task in the schedule is an "item" in "timer items", and only in that field. NEVER MAKE MORE THAN ONE JSON OBJECT. You are to NEVER edit the "Timer_Items" field. In that part of the response you are to instert
every task that is to be performed and the time alloted to it. the "Item" field is to contain the name of the activity, while the "Time Needed" 
contains the time alloted to it and the "Description" contains a brief description of how the time will be used. Make sure that you include ALL TASKS in the "Item" objects.
3. The "User" field should NEVER be changed, but the "Response" field should be filled with all the other information that isnt explicitly part of the schedule.
You are free to add as many {{"Item":{{"Time Needed":"Description"}}}} "Item" fields  inside the "Timer_ITems" field as necessary as long as they have a comma and space between them.
5. Make sure the response ALWAYS adheres to JSON formatting.
6. DO NOT PROVIDE A NEW RESPONSE WITH EVERY TASK. All prompts for the user must be short, and all be placed within ONE response. The same is true
with the items. Simply create multiple "Item" objects and place them one after the other in ONE response with an ", " separator, ONLY ever use as many as you need, no more and no less.
7. Make sure that you use ALL the data provided to you, do not add or distort it in any way and give me the json object as your response.
'''

prompted_fin = ChatPromptTemplate.from_template(FORMATTED_SCHEDULE)
prompts = prompted_fin.format(schedule = forms)
responses = model.invoke(prompts)
formses = f"{responses}"
print(formses) 