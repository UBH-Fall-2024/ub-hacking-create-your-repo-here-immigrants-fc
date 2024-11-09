from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate

model = Ollama(model = "llama3.2")

PROMPT_TEM = """
You are a personal Assistant for the user. You will be provided a list of tasks that need completing and a time frame, and your job is to
create a schedule for the user that meets the time frame and completes all tasks in the most efficient way possible. You can ask for clarification, but I want you to use any previous knowledge
you have on deep learning and the flow state, including concepts like the pomodoro technique and build the most efficient work flow you can.
Context:
{context}

User Question: {question}

Instructions:
1. Carefully analyze the timeframe, the provided context, and the user's tasks.
2. Make sure to use the provided context for planning ONLY. Do not let it affect the tasks at all. 
3. When creating a schedule, feel free to break up the tasks however you deem best, based on the provided context and ther perceived difficulty of the tasks.
4. Make sure to include breaks in the schedule as needed. Base the break timing and length on the various techniques in the context and on your own personal knowledge. 
5. If there is no provided context, please state "There is no provided context " followed by a response to the user that is made entirely on your own knowledge. Only do this if there is no context provided.
6. If you need further clarification on something, please ask the user for more information.
7. The tasks must be broken up in the most efficient way possible, Allowing the user to leverage deep work and the flow state to finish the tasks at the best of their ability.
8. When providing the schedule, include the time to work on the task, the task itself. Do the same for breaks.
9. Make sure to list some actvities the user can do during breaks that will allow them to rest, but also not lose focus.
10. Understand that some tasks may not be finished within the required time, so you do not necessarily need to expect bigger tasks to be finished within the given time limit.

Answer: Based on the list of tasks you provided, here is how you should structure your study session:
"""
context_texts = ""
quested_text = "I have an assignment to finish and I need to study for two tests. My assignment is a programming project, and I have to study for mty discrete math quiz and calc 2 midterm. I plan on spending 6 hours working on them today, how do I spread them out?"
prompted = ChatPromptTemplate.from_template(PROMPT_TEM)
prompt = prompted.format(context = context_texts, question = quested_text)
response = model.invoke(prompt)
forms = f"{response}"
print(forms) 